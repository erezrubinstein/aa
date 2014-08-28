from __future__ import division
from core.common.business_logic.service_entity_logic.store_helper import StoreHelper
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_rir, insert_test_address, insert_test_store, insert_test_geoprocessed_trade_area
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from core.common.utilities.include import *
import StringIO


class MainTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "main_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}
        self.remote_dirs = ['integration_test_files/', 'integration_test_files/chuck_norris/']
        self.local_dir = 'implementation/data/'
        self.main_params = Dependency("CoreAPIParamsBuilder").value
        self.store_helper = StoreHelper()

    def setUp(self):
        if "MAIN" in self.test_case.apps:
            self.main_access.call_delete_reset_database()
        if "MDS" in self.test_case.apps:
            self.mds_access.call_delete_reset_database()
        if "RDS" in self.test_case.apps:
            self.rds_access.call_delete_reset_database()
        if "WFS" in self.test_case.apps:
            self.wfs_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------------------##

    def main_test_get_entity_type_summary(self):

        company_id1 = insert_test_company()
        company_id2 = insert_test_company()
        company_id3 = insert_test_company()
        company_id4 = insert_test_company()

        main_summary = self.main_access.call_get_entity_type_summary("company")
        mds_summary = self.mds_access.call_get_entity_type_summary("company")
        self.test_case.assertEqual(main_summary, mds_summary)

    def main_test_get_entity_summary(self):

        company_id = insert_test_company()

        main_summary = self.main_access.call_get_entity_summary("company", company_id)
        mds_summary = self.mds_access.call_get_entity_summary("company", company_id)
        self.test_case.assertEqual(main_summary, mds_summary)

    def main_test_get_data_entities(self):

        company_ids = [insert_test_company(), insert_test_company(), insert_test_company(), insert_test_company()]

        fields = ["_id", "entity_type", "name", "data.ticker"]
        params = self.main_params.create_params(resource = "get_data_entities", fields = fields)
        companies = self.main_access.call_get_data_entities("company", params = params["params"])["rows"]

        self.test_case.assertEqual(len(companies), 4)
        for company in companies:
            self.test_case.assertIn(company["_id"], company_ids)
            self.test_case.assertEqual(company["name"], "UNITTESTCOMPANY")
            self.test_case.assertEqual(company["entity_type"], "company")
            self.test_case.assertEqual(company["data.ticker"], "")

    def main_test_get_data_entity_relationships(self):

        company_ids = [insert_test_company(), insert_test_company(), insert_test_company(), insert_test_company()]
        rir_ids = [insert_test_rir(self.context, company_id) for company_id in company_ids]

        for i in range(4):
            self.mds_access.call_add_link("company", company_ids[i], "company", "retail_input_record", rir_ids[i], "retail_input_record",
                                          "retail_input", self.context)

        fields = ["to._id", "to.entity_type", "to.name", "to.data.ticker",
                  "from._id", "from.entity_type", "from.name", "from.data.company_id"]
        params = self.main_params.create_params(resource = "get_data_entity_relationships", fields = fields)
        rels = self.main_access.call_get_data_entity_relationships("retail_input_record", "company", params = params["params"])["rows"]

        self.test_case.assertEqual(len(rels), 4)
        for rel in rels:
            self.test_case.assertIn(rel["to._id"], company_ids)
            self.test_case.assertEqual(rel["to.name"], "UNITTESTCOMPANY")
            self.test_case.assertEqual(rel["to.entity_type"], "company")
            self.test_case.assertEqual(rel["to.data.ticker"], "")
            self.test_case.assertIn(rel["from._id"], rir_ids)
            self.test_case.assertEqual(rel["from.name"], "UNIT_TEST_RIR")
            self.test_case.assertEqual(rel["from.entity_type"], "retail_input_record")
            self.test_case.assertIn(rel["from.data.company_id"], company_ids)

    def main_test_timing_1(self):

        self.logger.info("** Running main_test_timing_1")

        # Timing test 1: N entities, each linked to N entities of the same type

        # Get the original number of entities of the chosen type
        entity_type = self.test_case.tests["MDS"].entity_types[1]
        num_entities_orig = self.test_case.tests["MDS"].count_entities(entity_type)
        self.logger.info("Number of entities: %d", num_entities_orig)

        # Generate a complete graph of new entities
        num_entities = 20
        entity_ids = self.test_case.tests["MDS"].generate_complete_entity_graph(entity_type, num_entities)

        # Find all entities and fetch their linked entities for the selected entity type
        time_start = time.time()
        data = self.main_access.call_get_data_entity_relationships(entity_type, entity_type)
        time_end = time.time()
        time_diff = time_end - time_start
        self.logger.info("Entity relationships operation took %.2f seconds", time_diff)
        self.test_case.assertGreater(time_diff, 0)
        self.test_case.assertLess(time_diff, 1)

        self.test_case.assertGreaterEqual(set(r["to.entity_id"] for r in data), set(entity_ids))
        self.test_case.assertGreaterEqual(set(r["from.entity_id"] for r in data), set(entity_ids))

    #_________________________________________# File Tests #_____________________________________________#

    def main_test_file_upload_single(self):
        """
        Test that this main endpoint uploads the file to RDS and creates a file entity in MDS with
        the RDS file ID and additional data.
        """
        self.rds_access.call_delete_folder_by_name('root/')

        name = "root/trunk/branches/leaves/Banana.txt"
        test_files = {"Banana.txt": StringIO.StringIO("Banana")}
        additional_data = {"this is": "a banana"}

        mds_response = self.main_access.call_add_files("root/trunk/branches/leaves/",
                                                   self.context,
                                                   test_files,
                                                   additional_data)

        self.test_case.assertIn(name, mds_response)

        # test the additional data
        entity_fields = {
            "file": ["data"]
        }
        params = self.main_params.mds.create_params(resource="get_entity", entity_fields = entity_fields)['params']
        mds_file_data = self.main_access.mds.call_get_entity('file', mds_response[name], params)['data']
        self.test_case.assertIn('this is', mds_file_data)
        self.test_case.assertEqual(mds_file_data['this is'], additional_data['this is'])

        # check RDS
        rds_file_response = self.main_access.rds.call_get_file_by_name(name, self.context)
        self.test_case.assertEqual("Banana", rds_file_response.content)

        # check the RDS id is in the MDS file entity data
        rds_file_info_response = self.main_access.rds.call_get_file_info_by_name(name)
        self.test_case.assertEqual(rds_file_info_response['_id'], mds_file_data['rds_file_id'])

    def main_test_file_upload_multiple(self):

        # clear the mds database to get rid of rogue test files
        self.mds_access.call_delete_reset_database()
        self.rds_access.call_delete_folder_by_name('root/')

        names = ["root/trunk/branches/leaves/Banana.txt",
                 "root/trunk/branches/leaves/Mango.txt",
                 "root/trunk/branches/leaves/Papaya.txt"]

        test_files = {"Banana.txt": StringIO.StringIO("Banana"),
                      "Mango.txt": StringIO.StringIO("Mango"),
                      "Papaya.txt": StringIO.StringIO("Papaya")}

        file_contents = {"root/trunk/branches/leaves/Banana.txt": "Banana",
                         "root/trunk/branches/leaves/Mango.txt": "Mango",
                         "root/trunk/branches/leaves/Papaya.txt": "Papaya"}

        additional_data = {"this is": "a banana"}

        mds_response = self.main_access.call_add_files("root/trunk/branches/leaves/", self.context, test_files, additional_data)

        entity_fields = {"file": ["data"]}
        params = self.main_params.mds.create_params(resource="get_entity", entity_fields = entity_fields)['params']

        for name in names:
            self.test_case.assertIn(name, mds_response)
            # test the additional data
            mds_file_data = self.main_access.mds.call_get_entity('file', mds_response[name], params)['data']
            self.test_case.assertIn('this is', mds_file_data)
            self.test_case.assertEqual(mds_file_data['this is'], additional_data['this is'])

            # check RDS
            rds_file_response = self.main_access.rds.call_get_file_by_name(name, self.context)
            self.test_case.assertEqual(rds_file_response.content, file_contents[name])

            # check the RDS id is in the MDS file entity data
            rds_file_info_response = self.main_access.rds.call_get_file_info_by_name(name, self.context)
            self.test_case.assertEqual(rds_file_info_response['_id'], mds_file_data['rds_file_id'])

    def main_test_find_multiple_files(self):

        # clear the mds database to get rid of rogue test files
        self.mds_access.call_delete_reset_database()
        self.rds_access.call_delete_folder_by_name('root/')

        names = ["root/trunk/branches/leaves/Banana.txt",
                 "root/trunk/branches/leaves/Mango.txt",
                 "root/trunk/branches/leaves/Papaya.txt"]

        test_files = {"Banana.txt": StringIO.StringIO("Banana"),
                      "Mango.txt": StringIO.StringIO("Mango"),
                      "Papaya.txt": StringIO.StringIO("Papaya")}

        additional_data = {"this is": "a banana"}

        self.main_access.call_add_files("root/trunk/branches/leaves/", self.context, test_files, additional_data)

        files_info = self.main_access.call_find_files()

        self.test_case.assertEqual(len(files_info), 3)
        possible_indices = [0, 1, 2]
        found_indices = []
        for file_info in files_info:
            for name in names:
                if "name" in file_info and name == file_info["name"]:
                    self.test_case.assertIn("content_type", file_info)
                    self.test_case.assertIn("file_size", file_info)
                    found_indices.append(files_info.index(file_info))

        self.test_case.assertEqual(possible_indices, found_indices)

    def main_test_find_files_linked_to_entity(self):

        self.rds_access.call_delete_folder_by_name('root/')

        test_files = {"Banana.txt": StringIO.StringIO("Banana"),
                      "Mango.txt": StringIO.StringIO("Mango"),
                      "Papaya.txt": StringIO.StringIO("Papaya")}

        additional_data = {"this is": "a banana"}
        file_names_mds_ids = self.main_access.call_add_files("root/trunk/branches/leaves/",
                                                             self.context,
                                                             test_files,
                                                             additional_data)
        # create a RIR
        data = {"random": "data"}
        rir_id = self.mds_access.call_add_entity("retail_input_record", "test_record", data, self.context)

        # create links
        for name in file_names_mds_ids:
            link_data = self.mds_access.call_add_link("retail_input_record", rir_id, "retail_input_record",
                                                      "file", file_names_mds_ids[name], "retail_input_file",
                                                      "retail_input", self.context)

            self.test_case.assertEqual(link_data[0]["entity_id_from"], rir_id)
            self.test_case.assertEqual(link_data[0]["entity_id_to"], file_names_mds_ids[name])

        files_info = self.main_access.call_get_files_linked_from_entity("retail_input_record", rir_id, "retail_input",
                                                                        "retail_input_record", "retail_input_file")
        # ensure that we get back the right mds file ids
        self.test_case.assertEqual(len(files_info), 3)
        possible_indices = [0, 1, 2]
        found_indices = []
        for file_info in files_info:
            for name in file_names_mds_ids:
                if file_names_mds_ids[name] == file_info["to._id"]:
                    self.test_case.assertIn("to.content_type", file_info)
                    self.test_case.assertIn("to.file_size", file_info)
                    found_indices.append(files_info.index(file_info))

        self.test_case.assertEqual(possible_indices, found_indices)

    def main_test_post_files_linked_to_entity(self):

        self.rds_access.call_delete_folder_by_name('root/')
        names = ["root/trunk/branches/leaves/Banana.txt",
                 "root/trunk/branches/leaves/Mango.txt",
                 "root/trunk/branches/leaves/Papaya.txt"]

        test_files = {"Banana.txt": StringIO.StringIO("Banana"),
                      "Mango.txt": StringIO.StringIO("Mango"),
                      "Papaya.txt": StringIO.StringIO("Papaya")}

        # create a RIR
        data = {"random": "data"}
        path = "root/trunk/branches/leaves/"
        rir_id = self.mds_access.call_add_entity("retail_input_record", "test_record", data, self.context)
        links_info = self.main_access.call_upload_files_and_link_to_entity("retail_input_record", rir_id, "retail_input",
                                                                           "retail_input_record", "retail_input_file",
                                                                           path, self.context, test_files)
        # make sure the files got uploaded
        files_info = self.main_access.call_find_files()

        self.test_case.assertEqual(len(files_info), 3)
        possible_indices = [0, 1, 2]
        found_indices = []
        for file_info in files_info:

            for name in names:
                if "name" in file_info and name == file_info["name"]:
                    self.test_case.assertIn("content_type", file_info)
                    self.test_case.assertIn("file_size", file_info)
                    found_indices.append(files_info.index(file_info))

        self.test_case.assertEqual(possible_indices, found_indices)

        # ensure that the files got linked
        self.test_case.assertEqual(len(links_info), 6)
        possible_indices = [0, 1, 2, 3, 4, 5]
        found_indices = []

        for link_info in links_info:
            # check one direction
            if link_info["entity_id_from"] == rir_id:
                for file_info in files_info:
                    if file_info["_id"] == link_info["entity_id_to"]:
                        found_indices.append(links_info.index(link_info))
                        self.test_case.assertEqual(link_info["entity_role_to"], "retail_input_file")
                        self.test_case.assertEqual(link_info["entity_role_from"], "retail_input_record")
            # check the other direction
            else:
                for file_info in files_info:
                    if link_info["entity_id_from"] == file_info["_id"]:
                        found_indices.append(links_info.index(link_info))
                        self.test_case.assertEqual(link_info["entity_role_to"], "retail_input_record")
                        self.test_case.assertEqual(link_info["entity_role_from"], "retail_input_file")

        self.test_case.assertEqual(possible_indices, found_indices)

    #________________________________# Cache Cleanup Tests #_________________________________________#

    def main_test_delete_cache_when_create_entity(self):

        self.main_access.call_delete_preset_cache("delete_all")

        # create a company
        data = {"The": "system, is down"}
        entity_type = "company"
        name = "Rob"

        entity_id = self.main_access.mds.call_add_entity(entity_type, name, data, self.context)

        # query the company, request cache id back
        preset_cache_data = self.main_access.call_get_data_preset_companies()["rows"]
        # make sure Rob's Company is in the cache
        self.test_case.assertEqual(len(preset_cache_data), 1)

        self.test_case.assertEqual(preset_cache_data[0]["_id"], entity_id)
        self.test_case.assertEqual(preset_cache_data[0]["name"], "Rob")

        # add a new entity, query the preset cache, make sure both are in
        # create a company
        data = {"The": "system, is down"}
        entity_type = "company"
        name = "Oscelot"

        new_entity_id = self.main_access.mds.call_add_entity(entity_type, name, data, self.context)

        new_preset_cache_data = self.main_access.call_get_data_preset_companies()["rows"]

        self.test_case.assertEqual(len(new_preset_cache_data), 2)

        self.test_case.assertEqual(new_preset_cache_data[0]["_id"], entity_id)
        self.test_case.assertEqual(new_preset_cache_data[0]["name"], "Rob")

        self.test_case.assertEqual(new_preset_cache_data[1]["_id"], new_entity_id)
        self.test_case.assertEqual(new_preset_cache_data[1]["name"], "Oscelot")

    def main_test_delete_cache_when_update_entity(self):

        self.main_access.call_delete_preset_cache("delete_all")
        # create a company
        data = {"The": "system, is down"}
        entity_type = "company"
        name = "Rob"

        entity_id = self.main_access.mds.call_add_entity(entity_type, name, data, self.context)

        # query the company, request cache id back
        preset_cache_data = self.main_access.call_get_data_preset_companies()["rows"]
        # make sure Rob's Company is in the cache
        self.test_case.assertEqual(len(preset_cache_data), 1)

        self.test_case.assertEqual(preset_cache_data[0]["_id"], entity_id)
        self.test_case.assertEqual(preset_cache_data[0]["name"], "Rob")

        # now change the name.
        self.main_access.mds.call_update_entity("company", entity_id, self.context, "name", "Archer")

        # query the company, request cache id back
        new_preset_cache_data = self.main_access.call_get_data_preset_companies()["rows"]
        # make sure Rob's Company is in the cache
        self.test_case.assertEqual(len(preset_cache_data), 1)

        self.test_case.assertEqual(new_preset_cache_data[0]["_id"], entity_id)
        self.test_case.assertEqual(new_preset_cache_data[0]["name"], "Archer")

    def main_test_delete_cache_when_delete_entity(self):

        self.main_access.call_delete_preset_cache("delete_all")
        # create a company
        data = {"The": "system, is down"}
        entity_type = "company"
        name = "Rob"

        entity_id = self.main_access.mds.call_add_entity(entity_type, name, data, self.context)

        # query the company, request cache id back
        preset_cache_data = self.main_access.call_get_data_preset_companies()["rows"]
        # make sure Rob's Company is in the cache
        self.test_case.assertEqual(len(preset_cache_data), 1)

        self.test_case.assertEqual(preset_cache_data[0]["_id"], entity_id)
        self.test_case.assertEqual(preset_cache_data[0]["name"], "Rob")

        # add a new entity, query the preset cache, make sure both are in
        # create a company
        data = {"The": "system, is down"}
        entity_type = "company"
        name = "Oscelot"

        new_entity_id = self.main_access.mds.call_add_entity(entity_type, name, data, self.context)

        new_preset_cache_data = self.main_access.call_get_data_preset_companies()["rows"]

        self.test_case.assertEqual(len(new_preset_cache_data), 2)

        self.test_case.assertEqual(new_preset_cache_data[0]["_id"], entity_id)
        self.test_case.assertEqual(new_preset_cache_data[0]["name"], "Rob")

        self.test_case.assertEqual(new_preset_cache_data[1]["_id"], new_entity_id)
        self.test_case.assertEqual(new_preset_cache_data[1]["name"], "Oscelot")

        # now delete Rob
        self.main_access.mds.call_del_entity("company", entity_id)

        preset_cache_data_after_the_delete = self.main_access.call_get_data_preset_companies()["rows"]

        self.test_case.assertEqual(len(preset_cache_data_after_the_delete), 1)
        self.test_case.assertEqual(preset_cache_data_after_the_delete[0]["_id"], new_entity_id)
        self.test_case.assertEqual(preset_cache_data_after_the_delete[0]["name"], "Oscelot")

    #____________________________________# Add RIR Tests #_________________________________________#

    def main_test_add_rir(self):

        # clear the mds database to get rid of rogue test files
        self.mds_access.call_delete_reset_database()
        self.rds_access.call_delete_reset_database()

        # insert test company
        test_company_name = 'Oscelot'
        test_company_id = self.main_access.mds.call_add_entity('company',
                                                               test_company_name,
                                                               {'We will': 'get an office oscelot.'},
                                                               self.context)

        as_of_date = str(datetime.datetime(1990, 05, 18))
        files = {"Banana.txt": StringIO.StringIO("Banana")}

        data = {"company_id": test_company_id,
                "company_name": "Oscelot",
                "as_of_date": as_of_date,
                "street_number": '123',
                "street": 'Interrogation Room',
                "city": 'Nexus City',
                "state": 'Nexus',
                "zip": '00042',
                "phone": '42-42-42-42',
                "longitude": -1.0,
                "latitude": 1.0,
                "geo": [-1.0, 1.0],
                "country": None,
                "mall_name": None,
                "suite": None,
                "store_number": None,
                "store_format": None,
                "note": None,
                "store_url": None,
                "reason": None,
                "reason_source": None,
                "flagged_for_review": False,
                "review_comments": None,
                "source_type": "web",
                "source_name": "web",
                "source_id": "web",
                "as_of_date_is_opened_date": False}

        results = self.main_access.call_post_retail_input_add_one_record(data, files, self.context, async=False)

        rir_company_link = results['rir_company_links'][0]
        rir_file_links = results['rir_file_links'][0]
        company_file_links = results['company_file_links'][0]
        task_group = results["task_group"]

        self.test_case.assertEqual(rir_company_link['entity_type_from'], 'retail_input_record')

        rir_id = rir_company_link['entity_id_from']

        self.test_case.assertEqual(rir_company_link['entity_type_to'], 'company')
        self.test_case.assertEqual(rir_company_link['entity_id_to'], test_company_id)

        self.test_case.assertEqual(rir_company_link['entity_type_from'], 'retail_input_record')
        self.test_case.assertEqual(rir_company_link['relation_type'], 'retail_input')

        start = rir_company_link['interval'][0].replace('T', ' ')
        self.test_case.assertEqual(start, as_of_date)

        end = rir_company_link['interval'][1]
        self.test_case.assertEqual(end, None)

        self.test_case.assertEqual(rir_file_links['entity_type_from'], 'retail_input_record')
        self.test_case.assertEqual(rir_file_links['entity_id_from'], rir_id)
        self.test_case.assertEqual(rir_file_links['entity_type_to'], 'file')
        self.test_case.assertEqual(rir_file_links['entity_role_to'], 'file')
        self.test_case.assertEqual(rir_file_links['relation_type'], 'support_file')

        start = rir_file_links['interval'][0].replace('T', ' ')
        self.test_case.assertEqual(start, as_of_date)

        end = rir_file_links['interval'][1]
        self.test_case.assertEqual(end, None)

        mds_file_id = rir_file_links['entity_id_to']

        self.test_case.assertEqual(company_file_links['entity_type_from'], 'company')
        self.test_case.assertEqual(company_file_links['entity_id_from'], test_company_id)

        self.test_case.assertEqual(company_file_links['entity_type_to'], 'file')
        self.test_case.assertEqual(company_file_links['entity_id_to'], mds_file_id)
        self.test_case.assertEqual(company_file_links['entity_role_to'], 'retail_input_file')

        start = company_file_links['interval'][0].replace('T', ' ')
        self.test_case.assertEqual(start, as_of_date)

        end = company_file_links['interval'][1]
        self.test_case.assertEqual(end, None)

        # add specific tests, query the rir, query the file, make sure you get what you asked for
        rir_data = self.mds_access.call_get_entity('retail_input_record', rir_id)['data']
        self.test_case.assertEqual(rir_data['as_of_date'], as_of_date)
        self.test_case.assertEqual(rir_data['address'], '123 Interrogation Room')
        self.test_case.assertEqual(rir_data['city'], 'Nexus City')
        self.test_case.assertEqual(rir_data['state'], 'Nexus')
        self.test_case.assertEqual(rir_data['zip'], '00042')
        self.test_case.assertEqual(rir_data['phone'], '42-42-42-42')
        self.test_case.assertEqual(rir_data['geo'][0], -1.0)
        self.test_case.assertEqual(rir_data['geo'][1], 1.0)

        mds_file_data = self.main_access.call_find_files()[0]
        self.test_case.assertEqual(mds_file_data['name'], 'retail_input_records/%s/supporting_files/Banana.txt' % rir_id)

        parsing = task_group["summary"]["input_sourcing"]["parsing"]
        churn_matching = task_group["summary"]["input_sourcing"]["churn_matching"]
        churn_validation = task_group["summary"]["input_sourcing"]["churn_validation"]

        self.test_case.assertGreater(parsing["end_time"], str(datetime.datetime.now()))
        self.test_case.assertEqual(parsing["result"]["num_rirs"], 1)
        self.test_case.assertEqual(parsing["result"]["num_raw_records"], 1)
        self.test_case.assertEqual(parsing["result"]["num_stores_created"], 1)

        self.test_case.assertEqual(churn_matching["result"], {})
        self.test_case.assertEqual(churn_validation["result"], {})

###################################################################################################

    ### Tests for get_trade_areas preset and get_trade_area_by_id preset

    def main_test_get_trade_areas(self):
        trade_area_id_1 = insert_test_geoprocessed_trade_area(1, 1)
        trade_area_id_2 = insert_test_geoprocessed_trade_area(2, 1)

        params = {"sortIndex": 0,
                  "sortDirection": 1,
                  "fieldFilters": None,
                  "pageIndex": 0,
                  "pageSize": 20}

        response = self.main_access.call_get_preset(resource="/data/preset/trade_area", params=params,
                                                   context=self.context)
        self.test_case.assertIsNotNone(response)
        self.test_case.assertIsInstance(response, dict)
        self.test_case.assertIn("results", response)
        self.test_case.assertIsInstance(response["results"], list)

        #get list of returned store_ids
        response_trade_area_ids = [row[0] for row in response["results"]]

        self.test_case.assertEqual(len(response_trade_area_ids), 2)
        self.test_case.assertIn(trade_area_id_1, response_trade_area_ids)
        self.test_case.assertIn(trade_area_id_2, response_trade_area_ids)

    def main_test_get_trade_area_by_id(self):

        company_id = insert_test_company("ACOM", "All Company is Good Company", "retail_parent", "published")
        test_home_address_id = insert_test_address(0, 90, "1225", "Santa Street", "North Pole", "AC", "53110")
        test_away_address_id = insert_test_address(0, 90, "1212", "Banta Street", "Up the Pole", "AC", "53110")
        home_store_id = insert_test_store(company_id, [datetime.datetime(2013, 1, 1), datetime.datetime(2014, 1, 1)])
        away_store_id = insert_test_store(company_id, [datetime.datetime(2013, 1, 1), datetime.datetime(2014, 1, 1)])

        #link trade area's to addresses because we want to test data export also which needs store addresses
        self.mds_access.call_add_link("store", home_store_id, "subject",
                "address", test_home_address_id, "location", "address_assignment", self.context)
        self.mds_access.call_add_link("store", away_store_id, "subject",
                "address", test_away_address_id, "location", "address_assignment", self.context)

        trade_area_id = insert_test_geoprocessed_trade_area(home_store_id, away_store_id)

        self.mds_access.call_add_link("store", home_store_id, "home_store",
                "trade_area", trade_area_id, "trade_area", "store_trade_area", self.context)

        params = {"sortIndex": 0,
                  "sortDirection": 1,
                  "fieldFilters": None,
                  "pageIndex": 0,
                  "pageSize": 20}

        response = self.main_access.call_get_preset(resource="/data/preset/trade_area/%s" % trade_area_id,
                                                    params=params, context=self.context)

        self.test_case.assertIsNotNone(response)
        self.test_case.assertIsInstance(response, dict)

        self.test_case.assertEqual(response["home_store"][6], u"Santa Street")
        self.test_case.assertEqual(response["away_stores"][0][6], u"Banta Street")

        self.test_case.assertEqual(response["store_fields"],
            [u'Store Number', u'Store Format', u'Note', u'Phone', u'Company Name', u'Street Number', u'Street', \
             u'City', u'State', u'Zip', u'Latitude', u'Longitude', u'Suite', u'Shopping Center']
        )
        self.test_case.assertEqual(response["trade_area_data"][0], trade_area_id)
        self.test_case.assertEqual(response["trade_area_fields"],
            [u'Trade Area ID', u'Home Store ID', u'Company', u'Threshold', u'Street Number', u'Street', u'City', u'State', u'Zip', \
             u'Phone Number', u'Latitude', u'Longitude']
        )

        self.test_case.assertEqual(response["trade_area_shape"], [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
