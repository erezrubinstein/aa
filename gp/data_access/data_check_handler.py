from geoprocessing.business_logic.enums import DataCheckTypeRef
from common.utilities.sql import sql_execute, sql_execute_with_parameters
from geoprocessing.business_logic.business_objects.data_check import   DataCheckType
__author__ = 'erezrubinstein'

"""
This module represents various data access methods for dealing with the data check tables
"""

def get_sql_data_check_types():
    sql = '''SELECT data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold from data_check_types
                        WHERE sql is not null
                        ORDER BY data_check_type_id;'''
    data_check_types = {}
    rows = sql_execute(sql)
    for row in rows:
        data_check_types[row.data_check_type_id] = DataCheckType.standard_init(row.data_check_type_id, row.name,
            row.entity_type_id, row.sql, row.severity_level, row.fail_threshold)
    return data_check_types


def save_data_check(data_check):
    # insert data checks and get id
    data_check_id = __insert_data_check_and_get_id(data_check)
    data_check.data_check_id = data_check_id
    # insert into data check values
    __insert_into_data_check_values(data_check_id, data_check.data_check_values)
    return data_check_id


def execute_data_check_type_sql(data_check_type):
    if hasattr(data_check_type, 'parameters'):
        return sql_execute_with_parameters(data_check_type.parameters, data_check_type.sql)
    else:
        return sql_execute(data_check_type.sql)


def __insert_data_check_and_get_id(data_check):

    statement = '''INSERT INTO data_checks (data_check_type_id, check_done, bad_data_rows)
                   VALUES (?, GETUTCDATE(), ?)
                   '''
    parameters = [data_check.data_check_type_id, len(data_check.data_check_values)]
    sql_execute_with_parameters(parameters, statement)

    select_id_statement = '''SELECT @@IDENTITY'''
    return int(sql_execute(select_id_statement)[0][0])


def __insert_into_data_check_values(data_check_id, data_check_values):
    for data_check_value in data_check_values:
        statement = '''INSERT INTO data_check_values (data_check_id, value_type, expected_value, actual_value, entity_id)
                   VALUES (?, ?, ?, ?, ?)'''
        parameters = [data_check_id, data_check_value.value_type, data_check_value.expected_value,
                      data_check_value.actual_value, data_check_value.entity_id]
        sql_execute_with_parameters(parameters, statement)



def get_non_sql_data_check_rowcounts():
    statement = '''
            select dct.name as data_check_name, count(dc.data_check_type_id) as count
  from data_check_types dct
  left outer join data_checks dc
  on dct.data_check_type_id = dc.data_check_type_id
  where dct.data_check_type_id in (%s)
  group by dct.name
        ''' % ','.join(str(type) for type in DataCheckTypeRef.get_values())
    return sql_execute(statement)
