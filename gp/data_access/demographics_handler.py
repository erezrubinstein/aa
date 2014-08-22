import math
from common.utilities.sql import sql_execute
from geoprocessing.data_access.data_access_utilities import select_clean_up, insert_clean_up
from geoprocessing.data_access.period_handler import PeriodQueryHelper


__author__ = 'erezrubinstein'

"""
This module represents various data access methods for dealing with demographic related tables
"""


def get_seg_id(report_item):
    comm_seg_id = '''SELECT demographic_segment_id FROM demographic_segments
                     WHERE minimum_age %s AND maximum_age %s
                     AND gender = '%s' ''' % (select_clean_up(report_item.minimum_age),
                                              select_clean_up(report_item.maximum_age),
                                              report_item.gender)

    row = sql_execute(comm_seg_id)
    try:
        return row[0][0]
    except:
        return None

def get_data_item_id_by_name(name):

    # get the data item id since we can't store it as an enum - the consistency amongst retaildb_dev, _test, and build dbs is fubar
    statement = '''select data_item_id from data_items where name = '%s' ''' % name
    data_item_id = sql_execute(statement)[0][0]
    return data_item_id



def insert_demographics(trade_area, period_id, demographic_report_items, template_name, dataset_id):
    # create a trade area (unless already exists)

    # variables to keep track of
    big_num_insert = []
    big_str_insert = []

    # data items for this template
    # use set to keep them unique, just in case we have multiple data items here
    data_item_ids_num = set()
    data_item_ids_str = set()

    # this helps querying for a massive amount of data_items by leveraging a quick cache
    period_query_helper = PeriodQueryHelper()

    # insert segments and data items
    for report_item in demographic_report_items:

        # insert proper demographic segments if needed
        if template_name == 'Nexus Age by Sex Report' and report_item.gender is not None:
            report_item.segment_id = get_seg_id(report_item)

        # insert data items (unless already exists)
        select_data_item_by_name(report_item)

        # get period and target_period per data_item
        target_period_id = period_query_helper.select_period_id_for_year(report_item.year)

        # keep track of the above ids for the massive insert below (which links everything)
        if report_item.type_short is 'num':
            # verification for weird BA Online scenario
            if report_item.value == 'nan' or report_item.value == "NAN" or math.isnan(report_item.value):
                report_item.value = -1

            data_item_ids_num.add(report_item.data_item_id)
            big_num_insert.append(__get_temp_table_insert_statement(report_item, trade_area.trade_area_id, period_id, target_period_id, template_name))

        if report_item.type_short is 'str':
            data_item_ids_str.add(report_item.data_item_id)
            big_str_insert.append(__get_temp_table_insert_statement(report_item, trade_area.trade_area_id, period_id, target_period_id, template_name))

    # delete num & str values for this trade area and period
    # to clear out previous (i.e. bad) runs of data
    if data_item_ids_num:
        __delete_demographic_values(trade_area.trade_area_id, period_id, "num", data_item_ids_num, template_name)
    if data_item_ids_str:
        __delete_demographic_values(trade_area.trade_area_id, period_id, "str", data_item_ids_str, template_name)

    # combine the numvalues and stringvalues insert
    selects_unions = [('union all'.join(big_num_insert), 'num'), ('union all'.join(big_str_insert), 'str')]

    # insert all the mappings
    for selects_tup in selects_unions:
        selects = selects_tup[0]
        selects_type = selects_tup[1]
        if selects and len(selects) > 0:
            __insert_with_table_variable(selects_type, selects)


def select_data_item_by_name(report_item):


    comm_select = '''
                    SELECT data_item_id FROM data_items WHERE name = '%s';
                    ''' % report_item.name

    row = sql_execute(comm_select)

    if len(row) < 1:
        raise Exception ("no report item for %s" % report_item.name)

    report_item.data_item_id = int(row[0][0])


########################################################################################################
######################################### Internal Methods #############################################
########################################################################################################


def __delete_demographic_values(trade_area_id, period_id, del_type, data_item_ids, template_name):
    statement = '''
    DELETE FROM demographic_%svalues
    WHERE trade_area_id = %d and period_id = %d and template_name = '%s' and data_item_id in (%s);
    ''' % (del_type, trade_area_id, period_id, template_name, ','.join([str(d) for d in data_item_ids]))
    return sql_execute(statement)


def __get_temp_table_insert_statement(report_item, trade_area_id, period_id, target_period_id, template_name):
    # we clean up these selects with insert_clean_up because of this particular SQL syntax
    if isinstance(report_item.value, float):
        # special formatting for floats so that we don't have scientific format, which SQL doens't like...
        report_item.value = "%f" % report_item.value
    elif not isinstance(report_item.value, basestring):
        report_item.value = str(report_item.value)

    return '''
    SELECT %d AS trade_area_id, %d AS data_item_id, '%s' AS value, GETUTCDATE() AS created_at, GETUTCDATE() AS updated_at, %d AS period_id, %s AS segment_id,
        %s AS target_period_id, '%s' AS template_name
    ''' % (trade_area_id, report_item.data_item_id, report_item.value, int(period_id),
           insert_clean_up(report_item.segment_id), insert_clean_up(target_period_id), template_name)



def __insert_with_table_variable(selects_type, selects):
    # create dictionary to distinguish insert type between demographic_numvalues and demographics_strvalues
    selects_type_dict = {'num':'decimal (21, 8)', 'str':'varchar(250)'}

    # create big sql statement for inserting
    statement = '''declare @t table (trade_area_id int, data_item_id int, value %s, created_at datetime,
                        updated_at datetime, segment_id int, target_period_id int, period_id int, template_name varchar(100),
                        primary key (trade_area_id, data_item_id, period_id, target_period_id));

                    INSERT INTO @t (trade_area_id, data_item_id, value, created_at, updated_at, period_id, segment_id, target_period_id, template_name)
                    %s;

                    UPDATE m
                    SET m.value = t.value, m.updated_at = t.updated_at, m.segment_id = t.segment_id, m.target_period_id = t.target_period_id
                    FROM demographic_%svalues AS m
                    INNER JOIN @t t ON t.trade_area_id = m.trade_area_id and t.data_item_id = m.data_item_id and t.period_id = m.period_id and t.template_name = m.template_name
                    WHERE m.value != t.value or m.segment_id != t.segment_id or m.target_period_id != t.target_period_id;


                    INSERT INTO demographic_%svalues (trade_area_id, data_item_id, value, created_at, updated_at, period_id, segment_id, target_period_id, template_name)
                    SELECT trade_area_id, data_item_id, value, created_at, updated_at, period_id, segment_id, target_period_id, template_name
                    FROM @t t
                    WHERE NOT EXISTS
                    (
                        select m.demographic_%svalue_id
                        from demographic_%svalues AS m
                        where m.trade_area_id = t.trade_area_id and m.data_item_id = t.data_item_id
                            and m.period_id = t.period_id and m.target_period_id = t.target_period_id
                            and m.template_name = t.template_name
                    );''' % (selects_type_dict[selects_type], selects, selects_type, selects_type, selects_type, selects_type)


    # execute statement
    sql_execute(statement)
