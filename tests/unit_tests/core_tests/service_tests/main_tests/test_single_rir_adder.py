from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.business_logic.service_entity_logic.rir_helper import return_rir_entity_rec
from core.common.business_logic.service_entity_logic.address_helper import create_auto_parsed_address_from_rir_data
from core.common.business_logic.service_entity_logic.store_helper import StoreHelper
from core.common.utilities.helpers import generate_id
from core.service.svc_main.implementation.service_endpoints.endpoint_helpers.single_rir_adder import SingleRirAdder
import datetime
import mox


__author__ = 'vgold'


class SingleRirAdderTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(SingleRirAdderTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get several dependencies that we'll need in the class
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(SingleRirAdder)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.wfs = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()

        self.mock.address_helper = self.mox.CreateMockAnything()
        self.mock.rir_helper = self.mox.CreateMockAnything()
        self.mock.WorkflowTaskGroup = self.mox.CreateMockAnything()
        self.mock.RetailInputFileLoader = self.mox.CreateMockAnything()
        self.mock.BusinessEntity = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_single_rir_adder.py",
                        "user": {"user_id": 1, "is_generalist": False},
                        "team_industries": ["asdf"]}

        self.mock.context = self.context

    def doCleanups(self):

        super(SingleRirAdderTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # SingleRirAdder._create_rir()

    def test_create_rir(self):

        rir_helper_args = self.__get_rir_helper_args()
        rir = self.__make_rir(False, False)

        self.mock.rir_helper.return_rir_entity_rec(*rir_helper_args).AndReturn(rir)

        rir = self.__make_rir(False)
        self.mock.address_helper.create_auto_parsed_address_from_rir_data(rir["data"]).AndReturn(rir["data"]["auto_parsed_address"])

        rir_id = generate_id()
        self.mock.main_access.mds.call_add_entity_rec(rir, self.context).AndReturn(rir_id)

        self.mock.rir_data = rir["data"]

        self.mox.ReplayAll()
        result = SingleRirAdder._create_rir(self.mock)
        self.assertEqual(result, self.mock)

    ##########################################################################
    # SingleRirAdder._form_link_interval_and_data()

    def test_form_link_interval_and_data(self):

        rir = self.__make_rir()
        rir_link_interval = [rir["data"]["as_of_date"], None]
        rir_link_data = None

        self.mock.rir_id = rir["_id"]
        self.mock.rir_rec = rir

        self.mox.ReplayAll()
        result = SingleRirAdder._form_link_interval_and_data(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(rir_link_interval, self.mock.rir_link_interval)
        self.assertEqual(rir_link_data, self.mock.rir_link_data)

    ##########################################################################
    # SingleRirAdder._link_rir_to_company()

    def test_link_rir_to_company(self):

        rir = self.__make_rir()
        rir_link_interval = [rir["data"]["as_of_date"], None]
        rir_link_data = None

        rir_company_link = "rir_company_link"
        self.mock.main_access.mds.call_add_link('retail_input_record', rir["_id"], 'retail_input_record',
                                                'company', rir["data"]['company_id'], 'company',
                                                'retail_input', self.context, link_data = rir_link_data,
                                                link_interval = rir_link_interval).AndReturn(rir_company_link)

        self.mock.rir_id = rir["_id"]
        self.mock.rir_rec = rir
        self.mock.rir_link_interval = rir_link_interval
        self.mock.rir_link_data = rir_link_data

        self.mox.ReplayAll()
        result = SingleRirAdder._link_rir_to_company(self.mock)
        self.assertEqual(result, self.mock)

    ##########################################################################
    # SingleRirAdder._upload_file_and_link_rir()

    def test_upload_file_and_link_rir(self):

        rir = self.__make_rir()
        rir_link_interval = [rir["data"]["as_of_date"], None]
        rir_link_data = None

        files = "files"
        file_path = 'retail_input_records/%s/supporting_files/' % rir["_id"]
        additional_data = {
            'type': 'supporting_file',
            'source_url': rir["data"]["store_url"],
            'company_id': str(rir["data"]["company_id"]),
        }
        mds_file_id = generate_id()
        rir_file_link = [{"entity_id_to": mds_file_id}]
        self.mock.main_access.call_upload_files_and_link_to_entity('retail_input_record', rir["_id"], 'support_file',
                                                                   'target', 'file',
                                                                   file_path, self.context, files,
                                                                   link_interval = rir_link_interval,
                                                                   link_data = rir_link_data,
                                                                   additional_data = additional_data).AndReturn(rir_file_link)
        self.mock.main_access.mds.call_update_entity("retail_input_record", rir["_id"], self.context, "data.source_id", mds_file_id).AndReturn(None)
        self.mock.rir_id = rir["_id"]
        self.mock.rir_rec = rir
        self.mock.rir_files = files
        self.mock.rir_link_interval = rir_link_interval
        self.mock.rir_link_data = rir_link_data

        self.mox.ReplayAll()
        result = SingleRirAdder._upload_file_and_link_rir(self.mock)
        self.assertEqual(result, self.mock)

    ##########################################################################
    # SingleRirAdder._link_company_to_file()

    def test_link_company_to_file(self):

        rir = self.__make_rir()
        rir_link_interval = [rir["data"]["as_of_date"], None]
        rir_link_data = None

        mds_file_id = generate_id()
        company_file_link = "company_file_link"
        self.mock.mds_file_id = mds_file_id
        self.mock.main_access.mds.call_add_link('company', rir["data"]['company_id'], 'company',
                                                'file', mds_file_id, 'retail_input_file', 'retail_input', self.context,
                                                link_interval= rir_link_interval,
                                                link_data = rir_link_data).AndReturn(company_file_link)

        self.mock.rir_rec = rir
        self.mock.rir_id = rir["_id"]
        self.mock.rir_link_interval = rir_link_interval
        self.mock.rir_link_data = rir_link_data
        self.mock.rir_file_link = [{"entity_id_to": mds_file_id}]

        self.mox.ReplayAll()
        result = SingleRirAdder._link_company_to_file(self.mock)
        self.assertEqual(result, self.mock)

    ##########################################################################
    # SingleRirAdder._determine_whether_to_create_stores()

    def test_determine_whether_to_create_stores__no_results(self):

        rir = self.__make_rir()

        self.mock.main_access.mds.call_find_and_modify_entity("company", mox.IgnoreArg(), self.context).AndReturn([])

        self.mock.rir_rec = rir
        self.mock.create_stores = None

        self.mox.ReplayAll()
        result = SingleRirAdder._determine_whether_to_create_stores(self.mock)
        self.assertEqual(result, self.mock)
        self.assertFalse(self.mock.create_stores)

    def test_determine_whether_to_create_stores__one_result(self):

        rir = self.__make_rir()

        self.mock.main_access.mds.call_find_and_modify_entity("company", mox.IgnoreArg(), self.context).AndReturn([1])

        self.mock.rir_rec = rir
        self.mock.create_stores = None

        self.mox.ReplayAll()
        result = SingleRirAdder._determine_whether_to_create_stores(self.mock)
        self.assertEqual(result, self.mock)
        self.assertTrue(self.mock.create_stores)

    ##########################################################################
    # SingleRirAdder._get_matching_task_groups_by_unique_key()

    def test_get_matching_task_groups_by_unique_key__has_matches(self):

        self.mock.mds_file_id = 1
        # create fake data
        rir = self.__make_rir()
        results = [1, 2, 3]
        expected_params = {
            "query": {
                "unique_key.source_id": self.mock.mds_file_id,
                "unique_key.company_id": rir["data"]["company_id"],
                "unique_key.as_of_date": rir["data"]["as_of_date"],
                "summary.input_sourcing.churn_matching.is_available": { "$ne": False }
            }
        }

        # mock some members of the object
        self.mock.rir_rec = rir

        # begin recording
        self.mock.main_access.wfs.call_task_group_find(self.context, expected_params).AndReturn(results)

        # replay all
        self.mox.ReplayAll()

        # run and verify results
        result = SingleRirAdder._get_matching_task_groups_by_unique_key(self.mock)
        self.assertEqual(result, self.mock)
        self.assertEqual(self.mock.matching_task_groups, results)


    def test_get_matching_task_groups_by_unique_key__no_matches(self):

        self.mock.mds_file_id = 1

        # create fake data
        rir = self.__make_rir()
        timestamp = "chicken_woot"
        expected_params = {
            "query": {
                "unique_key.source_id": self.mock.mds_file_id,
                "unique_key.company_id": rir["data"]["company_id"],
                "unique_key.as_of_date": rir["data"]["as_of_date"],
                "summary.input_sourcing.churn_matching.is_available": { "$ne": False }
            }
        }

        # mock the rir_record and datetime
        self.mock.rir_rec = rir
        self.mox.StubOutWithMock(datetime, "datetime")

        # begin recording
        self.mock.main_access.wfs.call_task_group_find(self.context, expected_params).AndReturn([])
        datetime.datetime.utcnow().AndReturn(timestamp)

        # replay all
        self.mox.ReplayAll()

        # run and verify results
        result = SingleRirAdder._get_matching_task_groups_by_unique_key(self.mock)
        self.assertEqual(result, self.mock)
        self.assertEqual(self.mock.matching_task_groups, [])
        self.assertEqual(self.mock.task_group_unique_key["timestamp"], timestamp)

    ##########################################################################
    # SingleRirAdder._create_task_group_params()

    def test_create_task_group_params__matching_task_groups__create_stores(self):

        self.mox.StubOutWithMock(datetime, "datetime")
        timestamp = "timestamp"
        datetime.datetime.utcnow().AndReturn(timestamp)

        task_group = "task_group"
        task_group_params1 = "task_group_params1"
        self.mock._create_task_group_params_from_existing_task_group(task_group, timestamp).AndReturn(task_group_params1)

        task_group_params2 = "task_group_params2"
        self.mock._update_task_group_params_for_store_creation(task_group_params1).AndReturn(task_group_params2)

        self.mock.matching_task_groups = [task_group]
        self.mock.create_stores = True

        self.mox.ReplayAll()
        result = SingleRirAdder._create_task_group_params(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(self.mock.task_group_params, task_group_params2)

    def test_create_task_group_params__no_matching_task_groups__dont_create_stores(self):

        self.mox.StubOutWithMock(datetime, "datetime")
        timestamp = "timestamp"
        datetime.datetime.utcnow().AndReturn(timestamp)

        rir = self.__make_rir()

        unique_key = "unique_key"
        task_group = "task_group"
        self.mock.WorkflowTaskGroup.get_retail_curation_structure(unique_key, mox.IgnoreArg(), mox.IgnoreArg()).AndReturn(task_group)

        self.mock.main_access.wfs.call_task_group_new(task_group, self.context).AndReturn(task_group)

        task_group_params1 = "task_group_params1"
        self.mock._create_task_group_params_from_new_task_group(timestamp).AndReturn(task_group_params1)

        task_group_params2 = "task_group_params2"
        self.mock._update_task_group_params_for_store_creation(task_group_params1).AndReturn(task_group_params2)

        self.mock.rir_rec = rir
        self.mock.matching_task_groups = []
        self.mock.create_stores = True
        self.mock.task_group_unique_key = unique_key

        self.mox.ReplayAll()
        result = SingleRirAdder._create_task_group_params(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(self.mock.task_group_params, task_group_params2)

    ##########################################################################
    # SingleRirAdder._create_stores_and_addresses()

    def test_create_stores_and_addresses__create_stores(self):

        rir = self.__make_rir()
        self.mock.create_stores = True
        self.mock.rir_rec = rir
        self.mock.rir_id = rir["_id"]
        self.mock.async = True

        self.mock.store_helper = self.mox.CreateMock(StoreHelper)

        self.mock.store_helper.create_new_store(self.context, rir["_id"], async=True)

        self.mox.ReplayAll()
        result = SingleRirAdder._create_stores_and_addresses_if_necessary(self.mock)

        self.assertEqual(result, self.mock)

    def test_create_stores_and_addresses__dont_create_stores(self):

        self.mock.create_stores = False

        self.mox.ReplayAll()
        result = SingleRirAdder._create_stores_and_addresses_if_necessary(self.mock)

        self.assertEqual(result, self.mock)

    ##########################################################################
    # SingleRirAdder._update_task_group()

    def test_update_task_group(self):

        task_group = {"_id": generate_id()}
        task_group_params = "task_group_params"

        # Return value not used in method
        self.mock.main_access.wfs.call_update_task_group_id(task_group["_id"], self.context, task_group_params)

        new_task_group = "new_task_group"
        self.mock.main_access.wfs.call_get_task_group_id(task_group["_id"], self.context).AndReturn(new_task_group)

        self.mock.create_stores = True
        self.mock.task_group_params = task_group_params
        self.mock.task_group = task_group

        self.mox.ReplayAll()
        result = SingleRirAdder._update_task_group(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(new_task_group, self.mock.task_group)

    #----------------------------# Private Helper #----------------------------#

    @staticmethod
    def __get_rir_helper_args():

        return ("company_id", "company_name", "as_of_date", "street_number street", "city", "state", "zip_code",
                "phone", "longitude", "latitude", "country", "mall_name", "suite", "store_number",
                "store_format", "note", "store_url", "reason", "reason_source", "flagged_for_review",
                "review_comments", "source_type", "source_name", "source_id", 'as_of_date_is_opened_date')

    @classmethod
    def __make_rir(cls, include_id = True, include_auto_parsed_address = True):

        rir_helper_args = cls.__get_rir_helper_args()
        rir = return_rir_entity_rec(*rir_helper_args)

        if include_id:
            rir["_id"] = generate_id()

        rir["data"] = dict(rir["data"], longitude = rir["data"]["geo"][0], latitude = rir["data"]["geo"][1],
                           street_number = "street_number", street = "street")

        if include_auto_parsed_address:
            rir["data"]["auto_parsed_address"] = create_auto_parsed_address_from_rir_data(rir["data"])

        return rir

