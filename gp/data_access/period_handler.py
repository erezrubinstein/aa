from common.utilities.sql import sql_execute, sql_execute_with_parameters
from geoprocessing.business_logic.business_objects.period import Period

__author__ = 'erezrubinstein'




"""
This module represents various data access methods for dealing with periods
"""


def select_period_id_force_insert(start_date, end_date, duration_type):
    """
    This method selects a period id.
    If the period does not exist, the method inserts it
    """

    # if the period doesn't exist, insert it
    statement = """
IF NOT EXISTS
(
	SELECT period_id
	FROM periods
	WHERE period_start_date = ? and period_end_date = ? and duration_type_id = ?
)
BEGIN
	INSERT INTO periods (duration_type_id, period_start_date, period_end_date)
	VALUES (?, ?, ?)
END"""
    parameters = [start_date, end_date, duration_type, duration_type, start_date, end_date]
    sql_execute_with_parameters(parameters, statement)


    # select the period (should always exist because of the previous statement
    statement="""
SELECT period_id
FROM periods
WHERE period_start_date = ? and period_end_date = ? and duration_type_id = ?
"""
    parameters = [start_date, end_date, duration_type]
    return sql_execute_with_parameters(parameters, statement)[0][0]


def select_period_by_period_id(period_id):
    """
    This method gets properties of a period, given it's id
    """
    statement = """
    select period_id, duration_type_id, period_start_date, period_end_date
    from periods where period_id = ?
    """
    parameters = [period_id]
    row = sql_execute_with_parameters(parameters, statement)[0]
    return Period().standard_init(row.period_id, row.duration_type_id, row.period_start_date, row.period_end_date)


#####################################################################################################################
############################################## Helper Classes #######################################################
#####################################################################################################################

class PeriodDurations(object):
    """
    This is an enumeration, which represents the various period durations
    """
    YEAR = 1
    HALF_YEAR = 2
    QUARTER = 3
    MONTH = 4
    DAY = 5
    POINT_IN_TIME = 6
    ARBITRARY_LENGTH = 7


class PeriodQueryHelper(object):
    """
    This class helps find periods for a large variety of report items.
    It makes things faster by caching the periods, so that you don't double query the same year
    """
    def __init__(self):
        self.cached_periods = {}

    def select_period_id_for_year(self, year):
        if self.cached_periods.has_key(year):
            # if cached, return the cache
            period_id = self.cached_periods[year]
        else:
            # if not cached, query and add to the cache
            start_date = ''.join([str(year), '0101'])
            end_date = ''.join([str(year + 1), '0101'])
            period_id = select_period_id_force_insert(start_date, end_date, PeriodDurations.YEAR)
            self.cached_periods[year] = period_id

        return period_id
