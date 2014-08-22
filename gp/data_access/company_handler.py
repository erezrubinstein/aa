from common.utilities.sql import sql_execute, sql_execute_with_parameters
from geoprocessing.business_logic.business_objects.company import Company

__author__ = 'erezrubinstein'


"""
This module represents various data access methods for dealing with company tables
"""


def select_company_id_force_insert(company_name, database_name = None):

    statement = '''
                    IF NOT EXISTS
                    (
                        SELECT company_id
                        FROM companies
                        WHERE name = ?
                    )
                    BEGIN
                        INSERT INTO companies (name, created_at, updated_at)
                        VALUES (?, GETUTCDATE(), GETUTCDATE());
                    END'''
    # insert company (if doesn't exist)
    parameters = [company_name, company_name]
    sql_execute_with_parameters(parameters, statement, database_name = database_name)

    # select company_id
    statement = ''' SELECT company_id FROM companies WHERE name = ? '''
    row = sql_execute_with_parameters([company_name], statement, database_name = database_name)[0]

    return row.company_id


def update_company_ticker(company_id, ticker):
    statement = '''
                    UPDATE companies
                    SET ticker = ?, updated_at = GETUTCDATE()

                    WHERE company_id = ?'''
    parameters = [ticker, company_id]

    sql_execute_with_parameters(parameters, statement)


def select_sector_ids_for_company(company_id):
    statement = "SELECT sector_id FROM companies_sectors WHERE company_id = ?"

    rows = sql_execute_with_parameters([company_id], statement)
    sector_ids = [row.sector_id for row in rows]
    return sector_ids


def close_old_companies_sectors(sector_ids, assumed_end_date):
    for sector_id in sector_ids:
        statement = '''UPDATE companies_sectors SET assumed_end_date = ? WHERE sector_id = ?'''
        parameters = [assumed_end_date, sector_id]
        sql_execute_with_parameters(parameters, statement)


def insert_company_sectors(sectors, company_id, assumed_start_date):
    for sector in sectors:
        statement = '''

                        IF NOT EXISTS
                        (SELECT * FROM companies_sectors WHERE sector_id = ? AND company_id = ?)

                        INSERT INTO companies_sectors (sector_id, company_id, [primary], created_at, updated_at, assumed_start_date)
                        VALUES (?, ?, ?, GETUTCDATE(), GETUTCDATE(), ?)'''

        parameters = [sector.sector_id, company_id, sector.sector_id, company_id, sector.is_primary, assumed_start_date]
        sql_execute_with_parameters(parameters, statement)


def get_company_by_id(company_id):
    statement = "SELECT company_id, ticker, name, created_at, updated_at FROM companies WHERE company_id = ?"
    parameters = [company_id]
    row = sql_execute_with_parameters(parameters, statement)[0]
    return Company.standard_init(company_id, row.ticker, row.name, row.created_at, row.updated_at)


def select_all_companies():
    statement = "SELECT company_id, ticker, name, created_at, updated_at FROM companies"
    rows = sql_execute(statement)
    return [Company.standard_init(c.company_id, c.ticker, c.name, c.created_at, c.updated_at) for c in rows]