from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.business_logic.service_entity_logic.company_store_count_helper import get_store_count, get_num_active_stores
import mox
import datetime


__author__ = 'vgold'


class CompanyStoreCountHelperTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(CompanyStoreCountHelperTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to record
        self.main_access = self.mox.CreateMockAnything()
        self.main_access.wfs = self.mox.CreateMockAnything()
        self.main_access.mds = self.mox.CreateMockAnything()
        self.main_param = self.mox.CreateMockAnything()
        self.main_param.mds = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.cfg = Dependency("MoxConfig").value
        self.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {
            "user_id": 1,
            "source": "test_company_store_count_helper.py"}

    def doCleanups(self):

        super(CompanyStoreCountHelperTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # company_store_count_helper.get_store_count()

    def test_get_store_count(self):

        pass

    ##########################################################################
    # company_store_count_helper.get_num_active_stores()

    def test_get_num_active_stores(self):

        stores = [
            # open forever
            [0, None],
            
            # closed on 05/18/1990
            [0, [None, datetime.datetime(1990, 05, 18)]],
            
            # opened on 05/18/1990
            [0, [datetime.datetime(1990, 05, 18), None]],
            
            # opened on 11/13/1990
            [0, [datetime.datetime(1990, 11, 13), None]],
            
            # opened on 05/18/1991, closed on 05/18/1992
            [0, [datetime.datetime(1991, 05, 18), datetime.datetime(1992, 05, 18)]]
        ]
        
        # before 05/18/1990, count should be 2
        self.assertEqual(get_num_active_stores(stores, datetime.datetime(1989, 05, 18)), 2)
        self.assertEqual(get_num_active_stores(stores, '1989-05-18T00:00:00'), 2)

        # on 05/18/1990, count should still be 2 (one closed, one opened)
        self.assertEqual(get_num_active_stores(stores, datetime.datetime(1990, 05, 18)), 2)
        self.assertEqual(get_num_active_stores(stores, '1990-05-18T00:00:00'), 2)

        # on 05/19/1990, count should be still be 2
        self.assertEqual(get_num_active_stores(stores, datetime.datetime(1990, 05, 19)), 2)
        self.assertEqual(get_num_active_stores(stores, '1990-05-19T00:00:00'), 2)

        # on 11/13/1990, count should be 3 (store closes)
        self.assertEqual(get_num_active_stores(stores, datetime.datetime(1990, 11, 13)), 3)
        self.assertEqual(get_num_active_stores(stores, '1990-11-13T00:00:00'), 3)

        # on 05/18/1991, count should be 4 (store opens)
        self.assertEqual(get_num_active_stores(stores, datetime.datetime(1991, 05, 18)), 4)
        self.assertEqual(get_num_active_stores(stores, '1991-05-18T00:00:00'), 4)

        # on 05/18/1992, count should be 3 (store closes)
        self.assertEqual(get_num_active_stores(stores, datetime.datetime(1992, 05, 18)), 3)
        self.assertEqual(get_num_active_stores(stores, '1992-05-18T00:00:00'), 3)

        # on 05/19/1992, count should still be 3
        self.assertEqual(get_num_active_stores(stores, datetime.datetime(1992, 05, 19)), 3)
        self.assertEqual(get_num_active_stores(stores, '1992-05-19T00:00:00'), 3)


