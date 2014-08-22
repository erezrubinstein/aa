from geoprocessing.business_logic.enums import StoreChangeType
from common.utilities.sql import sql_execute_with_parameters

__author__ = 'spacecowboy'

# TODO: the modified_date is something specific - where do we get it from??





def save_stores_to_change_log(deleted_store_ids, changed_stores, file_created_date, source_file_id):

    statement = '''
                  INSERT INTO stores_change_log (store_id, log_date, change_type_id, comment, source_file_id, created_at, updated_at)
                  VALUES (?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE());
                  select scope_identity();'''

    for deleted_store_id in deleted_store_ids:
        parameters = [deleted_store_id, file_created_date, StoreChangeType.StoreClosed, None, source_file_id]
        sql_execute_with_parameters(parameters, statement)

    for store in changed_stores:
        parameters = [store.store_id, file_created_date, store.change_type, str(store.mismatched_parameters), source_file_id]
        sql_execute_with_parameters(parameters, statement)

    return source_file_id



def save_address_to_change_log(changed_address, file_created_date, source_file_id):

    statement = '''
                  INSERT INTO addresses_change_log (address_id, log_date, change_type_id, comment, source_file_id, created_at, updated_at)
                  VALUES (?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE());
                  select scope_identity();'''

    parameters = [changed_address.address_id, file_created_date, changed_address.change_type, str(changed_address.mismatched_parameters), source_file_id]
    address_change_log_id = sql_execute_with_parameters(parameters, statement)[0][0]

    for mismatch in changed_address.mismatched_parameters:
        value_type = mismatch[0]
        from_value = mismatch[1]
        to_value = mismatch[2]
        statement = '''insert into addresses_change_log_values (addresses_change_log_id, value_type, from_value, to_value, created_at, updated_at)
                       values (?,?,?,?, GETUTCDATE(), GETUTCDATE());'''
        parameters = [address_change_log_id, value_type, from_value, to_value]
        sql_execute_with_parameters(parameters, statement)

    return source_file_id
