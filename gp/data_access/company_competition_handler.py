from common.utilities.sql import sql_execute_with_parameters, sql_execute
from geoprocessing.data_access.data_access_utilities import insert_clean_up_string

__author__ = 'erezrubinstein'



def insert_company_competition(competitors, database_name = None):
    # create temp table to insert into.  This speeds up the insert tremendously because the SQL table insert will be done in batch with one transaction
    sql_statements = ['''
CREATE TABLE #competitive_companies(home_company_id int NOT NULL, away_company_id int NOT NULL, competition_strength float NOT NULL,
created_at datetime NOT NULL, updated_at datetime NOT NULL, assumed_start_date datetime NULL, assumed_end_date datetime NULL)''']

    for competitor in competitors:

        # create statement.  This is compacted into one line on purpose.  It seems to finish much faster on large data sets
        # ER - the below statements uses literals instead of parameters so because of an SQL Server parameter limitation
        sql_statements.append('''INSERT INTO #competitive_companies (home_company_id, away_company_id, competition_strength, created_at, updated_at, assumed_start_date, assumed_end_date)
VALUES (%d, %d, %s, GETUTCDATE(), GETUTCDATE(), '%s', %s);
''' % (competitor.home_company_id, competitor.away_company_id, str(competitor.competition_strength), competitor.start_date, insert_clean_up_string(competitor.end_date)))


    # add insert into real table statements (from temp table).
    # skip any record that has an active duplicate
    sql_statements.append('''
insert into competitive_companies (home_company_id, away_company_id, competition_strength, created_at, updated_at, assumed_start_date, assumed_end_date)
select temp_cc.home_company_id, temp_cc.away_company_id, temp_cc.competition_strength, temp_cc.created_at, temp_cc.updated_at, temp_cc.assumed_start_date, temp_cc.assumed_end_date
from #competitive_companies temp_cc
left join competitive_companies cc on cc.home_company_id = temp_cc.home_company_id and cc.away_company_id = temp_cc.away_company_id
    and cc.competition_strength = temp_cc.competition_strength and cc.assumed_end_date is null
where cc.home_company_id is null''')

    # add drop temp table statement
    sql_statements.append("drop table #competitive_companies")

    # join statements and execute
    big_statement = '; '.join(sql_statements)
    sql_execute(big_statement, database_name = database_name)


def select_all_open_competitive_companies_ids_for_company(company_id):
    statement = '''
                    SELECT
                        away_company_id
                    FROM competitive_companies
                    WHERE home_company_id = %d AND assumed_end_date is null''' % company_id

    rows = sql_execute(statement)
    competitive_company_ids = [row.away_company_id for row in rows]
    return competitive_company_ids


def close_old_company_competitors(away_company_ids, home_company_id, assumed_end_date):
    for competitor_id in away_company_ids:
        statement = "UPDATE competitive_companies SET assumed_end_date = ? WHERE home_company_id = ? AND away_company_id = ?"
        parameters = [assumed_end_date, home_company_id, competitor_id]
        sql_execute_with_parameters(parameters, statement)