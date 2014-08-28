from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import Dependency
from core.common.business_logic.service_entity_logic.rir_helper import get_as_of_date
import unittest
import logging

class RirHelperTests(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger('UNITTEST')
        register_common_mock_dependencies(logger=logger)
        self.main_access = Dependency('CoreAPIProvider').value
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        self.context = {}

    def tearDown(self):
        pass


    def test_get_linked_store_id(self):
        link_filters = [["retail_input_record", "store", "retail_input", { "fetch": False, "recursive": False } ]]
        link_fields = {
            "retail_input": ["entity_id_to"]
        }
        params = self.main_params.mds.create_params(resource="get_entity",
                                                    link_filters = link_filters,
                                                    link_fields = link_fields)['params']
        pass


    def test_get_as_of_date(self):
        self.main_access.mds.call_delete_reset_database()

        test_date = 'some date string'
        test_rir_id = 'are_you_getting_testy_with_me'
        test_rir = {
            '_id': test_rir_id,
            'data.as_of_date': test_date
        }
        entity_fields = {
            "retail_input_record": ["data.as_of_date"]
        }
        params = self.main_params.mds.create_params(resource="get_entity", entity_fields = entity_fields)['params']
        self.main_access.mds.add_params_entity('retail_input_record', test_rir_id, params, test_rir)

        #TODO: date should be parsed by ``core.common.utilities.helpers import parse_timestamp``
        #TODO: date should be a datetime.datetime with date.tzinfo == None
        #TODO: Dates go in as a datetime and come out as string - do not send in a string because the encoding will be inconsistent.
        date = get_as_of_date(self.context, test_rir_id)
        self.assertEqual(test_date, date)



if __name__ == '__main__':
    unittest.main()
