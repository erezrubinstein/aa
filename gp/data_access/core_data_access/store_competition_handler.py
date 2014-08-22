from common.utilities.date_utilities import normalize_start_date, normalize_end_date, parse_date
from common.utilities.inversion_of_control import Dependency
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance

__author__ = 'erezrubinstein'



# This module represents various data access methods for dealing with the competitive store tables
# ------------------------------------------------------------------------------------------------

def get_competitive_stores(trade_area_id):

    # get dependencies
    main_access = Dependency("CoreAPIProvider").value
    main_params_builder = Dependency("CoreAPIParamsBuilder").value

    # create parameters
    query = { "_id": trade_area_id }
    entity_fields = ["data.competitive_stores"]
    params = main_params_builder.mds.create_params(resource = "find_entities_raw", query = query, entity_fields = entity_fields)["params"]

    # run query
    trade_area = main_access.mds.call_find_entities_raw("trade_area", params)[0]

    # create store competition objects
    competitive_stores = []
    if "competitive_stores" in trade_area["data"]:
        for store_competition in trade_area["data"]["competitive_stores"]:

            # for backwards compatibility, understand that old data still understands opened_date, closed_date
            if "opened_date" in store_competition:
                start_date = normalize_start_date(parse_date(store_competition["opened_date"]))
                end_date = normalize_end_date(parse_date(store_competition["closed_date"]))
            else:
                start_date = normalize_start_date(parse_date(store_competition["start_date"]))
                end_date = normalize_end_date(parse_date(store_competition["end_date"]))

            competitive_stores.append(StoreCompetitionInstance.basic_init_with_dates(store_competition["away_store_id"], store_competition["away_company_id"],
                                                                                     start_date, end_date))

    return competitive_stores



def batch_upsert_competitive_stores(trade_area_id, competitive_stores):

    # get dependencies
    main_access = Dependency("CoreAPIProvider").value

    # create params
    query = { "_id": trade_area_id }
    update_operation = { "$set": { "data.competitive_stores": competitive_stores }}

    # create context
    context = {
        "source": "Geoprocessing integration test",
        "user_id": None
    }

    # update!
    main_access.mds.call_batch_update_entities("trade_area", query, update_operation, context, False)

