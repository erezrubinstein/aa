from datetime import datetime, date
from common.utilities.date_utilities import parse_date, END_OF_WORLD
from common.utilities.inversion_of_control import Dependency
from geoprocessing.business_logic.business_objects.monopoly import Monopoly
from geoprocessing.business_logic.enums import CompetitionType

__author__ = 'erezrubinstein'



# This module represents various data access methods for dealing with the monopoly tables
# ---------------------------------------------------------------------------------------


def select_active_monopoly_record(trade_area_id, batch_monopolies_list):

    # no need to select.  Just return the active record from this one.
    active_monopoly = _get_active_monopoly(batch_monopolies_list)

    if active_monopoly:
        return Monopoly(None, active_monopoly["monopoly_type"], trade_area_id, parse_date(active_monopoly["start_date"]), parse_date(active_monopoly["end_date"]))
    else:
        return


def insert_monopoly(monopoly_type, start_date, batch_monopolies_list):
    """
    This method is for backwards compatibility with the old SQL Server code.
    Instead of inserting a monopoly to the db, it simply adds it to a list, which later gets batch upserted (below)
    """

    # convert monopoly type id to the actual type
    try:
        monopoly_type_str = CompetitionType.reverse(monopoly_type)
    except:
        # if it's an exception, just cast to string.
        monopoly_type_str = str(monopoly_type)

    # create monopoly structure.  Always assume end date is END_OF_WORLD when inserting (i.e. current monopoly)
    new_monopoly = {
        "monopoly_type": monopoly_type_str,
        "start_date": start_date,
        "end_date": END_OF_WORLD
    }

    # add to list (no insert, just add to list)
    batch_monopolies_list.append(new_monopoly)


def close_monopoly_record(trade_area_id, end_date, batch_monopolies_list):
    """
    This method is for backwards compatibility with the old SQL Server code.
    Instead of closing the active monopoly in the db, it simply closes it in the list, which later gets batch upserted (below)
    """

    # get the active monopoly
    active_monopoly = _get_active_monopoly(batch_monopolies_list)

    # make sure to verify that the monopoly is closed (if it's there)
    if active_monopoly:

        # set the end date (will update object in the array since it's an instance)
        active_monopoly["end_date"] = end_date


def batch_upsert_monopolies(trade_area_id, batch_monopolies_list):

    # get dependencies
    main_access = Dependency("CoreAPIProvider").value

    # create parameters
    query = { "_id": trade_area_id }
    update_operations = { "$set": { "data.monopolies": batch_monopolies_list }}
    context = { "source": "Geoprocessing integration test", "user_id": None }

    # update
    main_access.mds.call_batch_update_entities("trade_area", query, update_operations, context, False)




# ----------------------------------------------- private methods ----------------------------------------------- #


def _get_active_monopoly(monopolies):
    results = filter(lambda m: _is_active_monopoly_end_date(m["end_date"]), monopolies)
    if len(results) == 1:
        return results[0]
    elif len(results) > 1:
        raise Exception("data error.  a trade_area should only have one monopoly.")
    else:
        return {}


def _is_active_monopoly_end_date(end_date):
    return end_date == END_OF_WORLD.isoformat() or end_date == END_OF_WORLD or end_date is None