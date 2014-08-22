from common.utilities.inversion_of_control import Dependency

__author__ = 'erezrubinstein'

class BaseCustomAnalyticsDataCheck(object):

    def __init__(self):

        # get some common dependencies
        self._gp_config = Dependency("Config").value

    def run(self):

        # run the data check
        results = self._run_data_check()

        # format the results
        formatted_results = self._format_results(results)

        # return the name and the formatted results
        return self._data_check_name(), formatted_results


    # ------------------- Template Methods ------------------- #

    def _data_check_name(self):
        raise NotImplementedError("yoyoma")

    def _run_data_check(self):
        raise NotImplementedError("yoyoma")

    def _format_results(self, results):
        raise NotImplementedError("yoyoma")