from geoprocessing.data_access.core_data_access.store_competition_handler import get_competitive_stores, batch_upsert_competitive_stores
from geoprocessing.data_access.core_data_access.monopoly_handler import select_active_monopoly_record, insert_monopoly, close_monopoly_record, batch_upsert_monopolies


__author__ = 'erezrubinstein'


class CoreDataRepository(object):
    """
    ER - This class should inherit from the regular data repository, but I chose not to on purpose.
    I do not want it to do any SQL and want it to raise an exception if any method that's not here is called.
    Let me know if you know of a more elegant solution ;)
    """
    ######################################## Competitive Stores Queries ################################################

    def get_competitive_stores(self, home_store_id, trade_area_id):
        # home store_id is ignored. it is for backwards compatibility
        return get_competitive_stores(trade_area_id)

    def batch_upsert_competitive_stores(self, trade_area_id, competitive_stores):
        return batch_upsert_competitive_stores(trade_area_id, competitive_stores)

    ############################################ Monopoly Queries ######################################################

    def select_active_monopoly_record(self, store_id, trade_area_id, batch_monopolies_list):
        # store_id is ignored.  it is for backwards compatibility
        return select_active_monopoly_record(trade_area_id, batch_monopolies_list)

    def insert_monopoly(self, store_id, monopoly_type_id, trade_area_id, start_date, batch_monopolies_list):
        # store_id, trade_area_id are ignored.  they are for backwards compatibility
        return insert_monopoly(monopoly_type_id,  start_date, batch_monopolies_list)

    def close_monopoly_record(self, store_id, trade_area_id, end_date, batch_monopolies_list):
        # store_id is ignored.  it is for backwards compatibility
        return close_monopoly_record(trade_area_id, end_date, batch_monopolies_list)

    def batch_upsert_monopolies(self, trade_area_id, batch_monopolies_list):
        batch_upsert_monopolies(trade_area_id, batch_monopolies_list)

    def delete_from_monopolies(self, store_id, trade_area_id):
        # this is for backwards compatibility. Core Data Repository does not need to delete.
        # Batch upsert takes care of that
        pass
