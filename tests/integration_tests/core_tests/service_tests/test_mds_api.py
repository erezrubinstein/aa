from __future__ import division
from tests.integration_tests.core_tests.service_tests.implementation.mds_test_collection import MDSTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_main.main_api import app as main_app
from core.service.svc_workflow.workflow_api import app as wfs_app
from tests.integration_tests.core_tests.service_tests.implementation.pair_entity_test_collection \
    import PairEntityTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.entity_hierarchy_creator_test_collection \
    import EntityHierarchyTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.mds_test_collection_with_verification \
    import MDSTestCollectionWithVerification
import unittest


__author__ = "vahram"


class Test_MDS_API(ServiceTestCase):
    """
    Test case for Main Data Service.
    See ServiceTestCase class for full documentation.
    """
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.svc_key = "MDS"
        cls.apps = {"MAIN": main_app, "MDS": mds_app, 'WFS': wfs_app}
        cls.test_colls = {
            "MDS": MDSTestCollection,
            "MDS_WITH_VERIFICATION": MDSTestCollectionWithVerification,
            "ENTITY_HIERARCHY": EntityHierarchyTestCollection,
            "PAIR_ENTITY": PairEntityTestCollection
        }

    def test_mds_aggregate(self):
        self.tests['MDS'].test_mds_aggregate()

    def test_mds_count(self):
        self.tests['MDS'].test_mds_count()

    def test_mds_aggregate__match_project(self):
        self.tests['MDS'].test_mds_aggregate__match_project()

    def test_mds_update__interval(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_update__interval()

    def test_mds_test_delete_most_correct_rir_first_in_chain(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_delete_most_correct_rir_first_in_chain()

    def test_mds_test_delete_most_correct_rir_middle_position(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_delete_most_correct_rir_middle_position()

    def test_mds_test_delete_most_correct_rir_last_in_chain(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_delete_most_correct_rir_last_in_chain()

    def test_mds_test_delete_most_correct_rir_only_one(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_delete_most_correct_rir_only_one()

    def test_mds_test_delete_store_by_id(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_delete_store_by_id()

    def test_mds_test_delete_store_by_id_old_encoders(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_delete_store_by_id_old_encoders()

    def test_mds_test_batch_insert_entities(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_batch_insert_entities()

    def test_mds_test_batch_insert_entity_with_links(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_batch_insert_entity_with_links()

    def test_mds_test_batch_update_entities(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_batch_update_entities()

    def test_mds_test_upsert__insert(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_mds_test_upsert__insert()

    def test_mds_test_upsert__insert__data_dot(self):
        self.tests["MDS_WITH_VERIFICATION"].test_mds_test_upsert__insert__data_dot()

    def test_mds_test_mds_test_upsert__insert__no_name(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_mds_test_upsert__insert__no_name()

    def test_mds_test_upsert__update(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_mds_test_upsert__update()

    def test_mds_test_find_raw__date_filter__one_date(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_find_raw__date_filter__one_date()

    def test_mds_test_find_raw__date_filter__date_range(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_find_raw__date_filter__date_range()

    def test_mds_test_find_raw__query_as_list__unwinding_bug(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_find_raw__query_as_list__unwinding_bug()

    def test_entity_hierarchy_creator(self):
        self.tests["ENTITY_HIERARCHY"].entity_hierarchy_creator()

    def test_pair_entity_create_delete(self):
        self.tests["PAIR_ENTITY"].pair_entity_create_delete()

    def test_pair_entity_delete_batch_raw__entity_ids(self):
        self.tests["PAIR_ENTITY"].pair_entity_delete_batch_raw__entity_ids()

    def test_pair_entity_delete_batch_raw__links_industry_ids(self):
        self.tests["PAIR_ENTITY"].pair_entity_delete_batch_raw__links_industry_ids()

    def test_pair_entity_synchronize(self):
        self.tests["PAIR_ENTITY"].pair_entity_synchronize()

    def test_industry_competes_with_itself(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_industry_competes_with_itself()

    def test_mds_test_batch_delete_entities(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_batch_delete_entities()

    def test_mds_add_audit(self):
        self.tests["MDS_WITH_VERIFICATION"].mds_test_mds_add_audit()

###################################################################################################

if __name__ == '__main__':
    unittest.main(verbosity=2)
