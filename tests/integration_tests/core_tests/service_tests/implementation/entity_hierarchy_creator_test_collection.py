from common.utilities.inversion_of_control import Dependency
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.entity_hierarchy_test_helper import create_companies_and_relationships


__author__ = 'vgold'


class EntityHierarchyTestCollection(ServiceTestCollection):

    def initialize(self, data_params = None):

        self.user_id = 'test@nexusri.com'
        self.source = "mds_entity_hierarchy_creator_test_collection.py"
        self.context = {
            "user_id": self.user_id,
            "source": self.source
        }

        # create params builder
        self.main_param = Dependency("CoreAPIParamsBuilder").value

    def setUp(self):
        # delete when starting
        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    #-----------------------------# Tests #-----------------------------#

    def entity_hierarchy_creator(self):

        create_companies_and_relationships(self)

        root_query = {
            "_id": self.company_id1
        }
        params = self.main_param.mds.create_params(resource="find_entity_hierarchy", root_query=root_query)["params"]
        results = self.mds_access.call_find_entity_hierarchy("company", params, self.context)
        self.test_case.assertEqual(len(results["entities"]), 19)

        root_query = {
            "_id": self.company_id4
        }
        params = self.main_param.mds.create_params(resource="find_entity_hierarchy", root_query=root_query)["params"]
        results = self.mds_access.call_find_entity_hierarchy("company", params, self.context)
        self.test_case.assertEqual(len(results["entities"]), 19)

        link_filters = [
            "_all",
            "_all",
            "_all",
            {
                "recursive": False
            }
        ]
        root_query = {
            "_id": self.company_id1
        }
        params = self.main_param.mds.create_params(resource="find_entity_hierarchy",
                                                   link_filters=link_filters, root_query=root_query)["params"]
        results = self.mds_access.call_find_entity_hierarchy("company", params, self.context)

        # Includes industry
        self.test_case.assertEqual(len(results["entities"]), 5)

        link_filters = [
            "_all",
            "_all",
            "_all",
            {
                "recursive": False,
                "entity_type_from": "company",
                "entity_type_to": "company"
            }
        ]
        root_query = {
            "_id": self.company_id1
        }
        params = self.main_param.mds.create_params(resource="find_entity_hierarchy",
                                                   link_filters=link_filters, root_query=root_query)["params"]
        results = self.mds_access.call_find_entity_hierarchy("company", params, self.context)

        # Excludes industry
        self.test_case.assertEqual(len(results["entities"]), 4)

