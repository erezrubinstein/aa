import unittest
from common.utilities.inversion_of_control import dependencies, Dependency
from geoprocessing.data_access.data_check_handler import get_sql_data_check_types
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import insert_test_store, delete_test_store, \
    delete_test_address, insert_test_address, insert_test_company, delete_test_company, delete_test_data_check, select_test_data_check, select_test_data_check_values
from geoprocessing.sql_data_checkers.standard_sql_data_checker import StandardSqlDataChecker
from geoprocessing.sql_data_checkers import sql_data_checker
from geoprocessing.business_logic.business_objects.data_check import DataCheck, DataCheckValue

__author__ = 'jkim'

class TestSqlDataChecker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        register_concrete_dependencies(False)
        cls._SQL_data_repository = Dependency("DataRepository").value
        cls._config = Dependency("Config").value

        # silence logger for test
        Dependency("LogManager").value._logger.setLevel(10000)

        # store temp default db settings to reset config on teardown
        cls._default_db_server = cls._config.db_server
        cls._default_db_database = cls._config.db_database
        cls._default_db_username = cls._config.db_username
        cls._default_db_password = cls._config.db_password

        # inject bad data integration test server settings
        cls._config.db_server = cls._config.bad_data_integration_test_db_server
        cls._config.db_database = cls._config.bad_data_integration_test_db_database
        cls._config.db_username = cls._config.bad_data_integration_test_db_username
        cls._config.db_password = cls._config.bad_data_integration_test_db_password

        # declare dict to store data_check_types
        cls.data_check_types = get_sql_data_check_types()


    @classmethod
    def tearDownClass(cls):
        dependencies.clear()

        # reset config default db settings
        cls._config.db_server = cls._default_db_server
        cls._config.db_database = cls._default_db_database
        cls._config.db_username = cls._default_db_username
        cls._config.db_password = cls._default_db_password


    def test_run_all_sql_data_checks(self):
        """
        Run all the sql data checks and make sure an exception is not thrown
        due to schema changes or bad queries, etc
        """

        # we should run all the data checks through the main function to support
        # different sql data checker classes we may create in the future
        results = sql_data_checker.main()

        # if any data check threw an exception, its value in the dict will be None
        failed_data_check_ids = []
        for data_check_type in sorted(results, key=lambda key: key.data_check_type_id):
            if results[data_check_type] is None:
                failed_data_check_ids.append(data_check_type.data_check_type_id)

        # I want it to display all failed checks so I'm not doing a self.assertEqual(0, len(failed_data_check_ids))
        if len(failed_data_check_ids) is not 0:
            self.fail('Failed SQL Data Check IDs: %s' % [str(s) for s in failed_data_check_ids])


    def test_run_data_checks_id_2(self):
    # test data_check_type_id = 2
    # stores with neither competition relationships nor are flagged as monopolies
    # TODO: finish this test
        data_check_type_id = 2
        store_id = None
        competitor_company_id = None
        address_id = None
        company_id = None
        data_check = None
        try:
            company_id = insert_test_company()
            address_id = insert_test_address(-1, 1)
            store_id = insert_test_store(company_id, address_id)
#            #new_address_id = insert_test_address(new_store_id, -1, 1)
#            #store = Store(store_id, company_id, -1, 1)
#            #create fake company and stores for competitors
#            competitor_company_id = insert_test_company('UNITTESTCOMPETITOR1')
#            #create fake competitor structure
#            insert_test_competitor(company_id, competitor_company_id)
#            #fake company 1 has 2 stores and fake company 2 has one store
#            competitor_store_id = insert_test_store(competitor_company_id)
            data_check = StandardSqlDataChecker(self.data_check_types[data_check_type_id]).run_data_check()
            data_check_from_db = self.get_data_check(data_check.data_check_id)
            self.assertTrue(self.check_entity_id_in_data_check_values(store_id, data_check_from_db.data_check_values))
        except:
            raise
        finally:
            if store_id is not None:
                delete_test_store(store_id)
            if address_id is not None:
                delete_test_address(address_id)
#            if company_id is not None:
#                delete_test_competitors(company_id)
#            if competitor_company_id is not None:
#                delete_test_company(competitor_company_id)
            if company_id is not None:
                delete_test_company(company_id)
            if data_check is not None:
                delete_test_data_check(data_check.data_check_id)


    def test_data_check_type_id_3(self):
    # test data_check_type_id = 3
    # duplicate addresses
        data_check_type_id = 3
        address_id = None
        dupe_address_id = None
        data_check = None
        try:
            address_id = insert_test_address(-1, 1)
            dupe_address_id = insert_test_address(-1, 1)
            data_check = StandardSqlDataChecker(self.data_check_types[data_check_type_id]).run_data_check()
            data_check_from_db = self.get_data_check(data_check.data_check_id)
            self.assertTrue(data_check_from_db.bad_data_rows >= 2)
            self.assertTrue(self.check_entity_id_in_data_check_values(address_id, data_check_from_db.data_check_values))
            self.assertTrue(self.check_entity_id_in_data_check_values(dupe_address_id, data_check_from_db.data_check_values))
        except:
            raise
        finally:
            #delete fake data
            if address_id is not None:
                delete_test_address(address_id)
            if dupe_address_id is not None:
                delete_test_address(dupe_address_id)
            if data_check is not None:
                delete_test_data_check(data_check.data_check_id)



    def test_run_data_checks_id_4(self):
    # test data_check_type_id = 4
    # stores with no basic demographic stats
        data_check_type_id = 4
        store_id = None
        address_id = None
        company_id = None
        data_check = None
        try:
            company_id = insert_test_company()
            address_id = insert_test_address(-1, 1)
            store_id = insert_test_store(company_id, address_id)
            data_check = StandardSqlDataChecker(self.data_check_types[data_check_type_id]).run_data_check()
            data_check_from_db = self.get_data_check(data_check.data_check_id)
            self.assertTrue(self.check_entity_id_in_data_check_values(store_id, data_check_from_db.data_check_values))
        except:
            raise
        finally:
            if store_id is not None:
                delete_test_store(store_id)
            if address_id is not None:
                delete_test_address(address_id)
            if company_id is not None:
                delete_test_company(company_id)
            if data_check is not None:
                delete_test_data_check(data_check.data_check_id)



#    def test_run_data_checks_id_5(self):
#    # test data_check_type_id = 5
#    # stores with NO demographic values
#    # TODO: finish this test
#        data_check_type_id = 5
#        store_id = None
#        address_id = None
#        company_id = None
#        data_check = None
#        try:
#            company_id = insert_test_company()
#            address_id = insert_test_address(-1, 1)
#            store_id = insert_test_store(company_id, address_id)
#            data_check = StandardSqlDataChecker(self.data_check_types[data_check_type_id]).run_data_check()
#            data_check_from_db = self.get_data_check(data_check.data_check_id)
#            self.assertTrue(self.check_entity_id_in_data_check_values(store_id, data_check_from_db.data_check_values))
#        except:
#            raise
#        finally:
#            if store_id is not None:
#                delete_test_store(store_id)
#            if address_id is not None:
#                delete_test_address(address_id)
#            if company_id is not None:
#                delete_test_company(company_id)
#            if data_check is not None:
#                delete_test_data_check(data_check.data_check_id)



    def test_run_data_checks_id_6(self):
    # test data_check_type_id = 6
    # stores with no trade areas
        data_check_type_id = 6
        store_id = None
        address_id = None
        company_id = None
        data_check = None
        try:
            company_id = insert_test_company()
            address_id = insert_test_address(-1, 1)
            store_id = insert_test_store(company_id, address_id)
            data_check = StandardSqlDataChecker(self.data_check_types[data_check_type_id]).run_data_check()
            data_check_from_db = self.get_data_check(data_check.data_check_id)
            self.assertTrue(self.check_entity_id_in_data_check_values(store_id, data_check_from_db.data_check_values))
        except:
            raise
        finally:
            if store_id is not None:
                delete_test_store(store_id)
            if address_id is not None:
                delete_test_address(address_id)
            if company_id is not None:
                delete_test_company(company_id)
            if data_check is not None:
                delete_test_data_check(data_check.data_check_id)



    def test_run_data_checks_id_7(self):
    # test data_check_type_id = 7
    # US addresses with less than 5 digit postal_areas
        data_check_type_id = 7
        address_id = None
        data_check = None
        try:
            address_id = insert_test_address(-1, 1, postal_area = 1111)
            data_check = StandardSqlDataChecker(self.data_check_types[data_check_type_id]).run_data_check()
            data_check_from_db = self.get_data_check(data_check.data_check_id)
            self.assertTrue(self.check_entity_id_in_data_check_values(address_id, data_check_from_db.data_check_values))
        except:
            raise
        finally:
            if address_id is not None:
                delete_test_address(address_id)
            if data_check is not None:
                delete_test_data_check(data_check.data_check_id)




#    def test_run_data_checks_id_8(self):
#    # test data_check_type_id = 8
#    # stores with same number of competitions in different trade area thresholds
#        # TODO: this test
#        data_check_type_id = 8
#        try:
#        except:
#            raise
#        finally:




    def test_run_data_checks_id_13(self):
    # test data_check_type_id = 13
    # addresses with leading/trailing spaces in the street
        data_check_type_id = 13
        address_id = None
        address_id_left_space = None
        address_id_right_space = None
        address_id_left_right_space = None
        data_check = None
        try:
            address_id = insert_test_address(-1, 1)
            address_id_left_space = insert_test_address(-1, 1, street=' UNITTEST')
            address_id_right_space = insert_test_address(-1, 1, street='UNITTEST ')
            address_id_left_right_space = insert_test_address(-1, 1, street=' UNITTEST ')
            data_check = StandardSqlDataChecker(self.data_check_types[data_check_type_id]).run_data_check()
            data_check_from_db = self.get_data_check(data_check.data_check_id)
            self.assertTrue(data_check_from_db.bad_data_rows >= 3)
            self.assertTrue(self.check_entity_id_in_data_check_values(address_id_left_space, data_check_from_db.data_check_values))
            self.assertTrue(self.check_entity_id_in_data_check_values(address_id_right_space, data_check_from_db.data_check_values))
            self.assertTrue(self.check_entity_id_in_data_check_values(address_id_left_right_space, data_check_from_db.data_check_values))
            self.assertFalse(self.check_entity_id_in_data_check_values(address_id, data_check_from_db.data_check_values))
        except:
            raise
        finally:
            if address_id is not None:
                delete_test_address(address_id)
            if address_id_left_space is not None:
                delete_test_address(address_id_left_space)
            if address_id_right_space is not None:
                delete_test_address(address_id_right_space)
            if address_id_left_right_space is not None:
                delete_test_address(address_id_left_right_space)
            if data_check is not None:
                delete_test_data_check(data_check.data_check_id)


    def test_run_data_checks_id_14(self):
    # test data_check_type_id = 14
    # addresses with leading/trailing spaces in the municipality
        data_check_type_id = 14
        address_id = None
        address_id_left_space = None
        address_id_right_space = None
        address_id_left_right_space = None
        data_check = None
        try:
            address_id = insert_test_address(-1, 1)
            address_id_left_space = insert_test_address(-1, 1, municipality=' UNITTEST')
            address_id_right_space = insert_test_address(-1, 1, municipality='UNITTEST ')
            address_id_left_right_space = insert_test_address(-1, 1, municipality=' UNITTEST ')
            data_check = StandardSqlDataChecker(self.data_check_types[data_check_type_id]).run_data_check()
            data_check_from_db = self.get_data_check(data_check.data_check_id)
            self.assertTrue(data_check_from_db.bad_data_rows >= 3)
            self.assertTrue(self.check_entity_id_in_data_check_values(address_id_left_space, data_check_from_db.data_check_values))
            self.assertTrue(self.check_entity_id_in_data_check_values(address_id_right_space, data_check_from_db.data_check_values))
            self.assertTrue(self.check_entity_id_in_data_check_values(address_id_left_right_space, data_check_from_db.data_check_values))
            self.assertFalse(self.check_entity_id_in_data_check_values(address_id, data_check_from_db.data_check_values))
        except:
            raise
        finally:
            if address_id is not None:
                delete_test_address(address_id)
            if address_id_left_space is not None:
                delete_test_address(address_id_left_space)
            if address_id_right_space is not None:
                delete_test_address(address_id_right_space)
            if address_id_left_right_space is not None:
                delete_test_address(address_id_left_right_space)
            if data_check is not None:
                delete_test_data_check(data_check.data_check_id)


    def test_run_data_checks_id_15(self):
    # test data_check_type_id = 15
    # addresses with leading/trailing spaces in the governing_district
        # !!! ER - I'm commenting this out because of the new foreign key in the addresses table
        pass
#        data_check_type_id = 15
#        address_id = None
#        address_id_left_space = None
#        address_id_right_space = None
#        address_id_left_right_space = None
#        data_check = None
#        try:
#            address_id = insert_test_address(-1, 1)
#            address_id_left_space = insert_test_address(-1, 1, governing_district=' NJ')
#            address_id_right_space = insert_test_address(-1, 1, governing_district='NJ ')
#            address_id_left_right_space = insert_test_address(-1, 1, governing_district=' NJ ')
#            data_check = StandardSqlDataChecker(self.data_check_types[data_check_type_id]).run_data_check()
#            data_check_from_db = self.get_data_check(data_check.data_check_id)
#            self.assertTrue(data_check_from_db.bad_data_rows >= 3)
#            self.assertTrue(self.check_entity_id_in_data_check_values(address_id_left_space, data_check_from_db.data_check_values))
#            self.assertTrue(self.check_entity_id_in_data_check_values(address_id_right_space, data_check_from_db.data_check_values))
#            self.assertTrue(self.check_entity_id_in_data_check_values(address_id_left_right_space, data_check_from_db.data_check_values))
#            self.assertFalse(self.check_entity_id_in_data_check_values(address_id, data_check_from_db.data_check_values))
#        except:
#            raise
#        finally:
#            if address_id is not None:
#                delete_test_address(address_id)
#            if address_id_left_space is not None:
#                delete_test_address(address_id_left_space)
#            if address_id_right_space is not None:
#                delete_test_address(address_id_right_space)
#            if address_id_left_right_space is not None:
#                delete_test_address(address_id_left_right_space)
#            if data_check is not None:
#                delete_test_data_check(data_check.data_check_id)


    def test_run_data_checks_id_16(self):
    # test data_check_type_id = 16
    # addresses with leading/trailing spaces in the postal_area
        data_check_type_id = 16
        address_id = None
        address_id_left_space = None
        address_id_right_space = None
        address_id_left_right_space = None
        data_check = None
        try:
            address_id = insert_test_address(-1, 1)
            address_id_left_space = insert_test_address(-1, 1, postal_area=' UNITTEST')
            address_id_right_space = insert_test_address(-1, 1, postal_area='UNITTEST ')
            address_id_left_right_space = insert_test_address(-1, 1, postal_area=' UNITTEST ')
            data_check = StandardSqlDataChecker(self.data_check_types[data_check_type_id]).run_data_check()
            data_check_from_db = self.get_data_check(data_check.data_check_id)
            self.assertTrue(data_check_from_db.bad_data_rows >= 3)
            self.assertTrue(self.check_entity_id_in_data_check_values(address_id_left_space, data_check_from_db.data_check_values))
            self.assertTrue(self.check_entity_id_in_data_check_values(address_id_right_space, data_check_from_db.data_check_values))
            self.assertTrue(self.check_entity_id_in_data_check_values(address_id_left_right_space, data_check_from_db.data_check_values))
            self.assertFalse(self.check_entity_id_in_data_check_values(address_id, data_check_from_db.data_check_values))
        except:
            raise
        finally:
            if address_id is not None:
                delete_test_address(address_id)
            if address_id_left_space is not None:
                delete_test_address(address_id_left_space)
            if address_id_right_space is not None:
                delete_test_address(address_id_right_space)
            if address_id_left_right_space is not None:
                delete_test_address(address_id_left_right_space)
            if data_check is not None:
                delete_test_data_check(data_check.data_check_id)


    def test_run_data_checks_id_17(self):
    # test data_check_type_id = 17
    # companies with leading/trailing spaces in the ticker
        data_check_type_id = 17
        company_id = None
        company_id_left_space = None
        company_id_right_space = None
        company_id_left_right_space = None
        data_check = None
        try:
            company_id = insert_test_company()
            company_id_left_space = insert_test_company(ticker=' UNITTEST')
            company_id_right_space = insert_test_company(ticker='UNITTEST ')
            company_id_left_right_space = insert_test_company(ticker=' UNITTEST ')
            data_check = StandardSqlDataChecker(self.data_check_types[data_check_type_id]).run_data_check()
            data_check_from_db = self.get_data_check(data_check.data_check_id)
            self.assertTrue(data_check_from_db.bad_data_rows >= 3)
            self.assertTrue(self.check_entity_id_in_data_check_values(company_id_left_space, data_check_from_db.data_check_values))
            self.assertTrue(self.check_entity_id_in_data_check_values(company_id_right_space, data_check_from_db.data_check_values))
            self.assertTrue(self.check_entity_id_in_data_check_values(company_id_left_right_space, data_check_from_db.data_check_values))
            self.assertFalse(self.check_entity_id_in_data_check_values(company_id, data_check_from_db.data_check_values))
        except:
            raise
        finally:
            if company_id is not None:
                delete_test_company(company_id)
            if company_id_left_space is not None:
                delete_test_company(company_id_left_space)
            if company_id_right_space is not None:
                delete_test_company(company_id_right_space)
            if company_id_left_right_space is not None:
                delete_test_company(company_id_left_right_space)
            if data_check is not None:
                delete_test_data_check(data_check.data_check_id)


    def test_run_data_checks_id_18(self):
    # test data_check_type_id = 18
    # companies with leading/trailing spaces in the name
        data_check_type_id = 18
        company_id = None
        company_id_left_space = None
        company_id_right_space = None
        company_id_left_right_space = None
        data_check = None
        try:
            company_id = insert_test_company()
            company_id_left_space = insert_test_company(name=' UNITTEST')
            company_id_right_space = insert_test_company(name='UNITTEST ')
            company_id_left_right_space = insert_test_company(name=' UNITTEST ')
            data_check = StandardSqlDataChecker(self.data_check_types[data_check_type_id]).run_data_check()
            data_check_from_db = self.get_data_check(data_check.data_check_id)
            self.assertTrue(data_check_from_db.bad_data_rows >= 3)
            self.assertTrue(self.check_entity_id_in_data_check_values(company_id_left_space, data_check_from_db.data_check_values))
            self.assertTrue(self.check_entity_id_in_data_check_values(company_id_right_space, data_check_from_db.data_check_values))
            self.assertTrue(self.check_entity_id_in_data_check_values(company_id_left_right_space, data_check_from_db.data_check_values))
            self.assertFalse(self.check_entity_id_in_data_check_values(company_id, data_check_from_db.data_check_values))
        except:
            raise
        finally:
            if company_id is not None:
                delete_test_company(company_id)
            if company_id_left_space is not None:
                delete_test_company(company_id_left_space)
            if company_id_right_space is not None:
                delete_test_company(company_id_right_space)
            if company_id_left_right_space is not None:
                delete_test_company(company_id_left_right_space)
            if data_check is not None:
                delete_test_data_check(data_check.data_check_id)


    def test_run_data_checks_id_19(self):
    # test data_check_type_id = 19
    # stores with leading/trailing spaces in the phone_number
        data_check_type_id = 19
        store_id = None
        store_id_left_space = None
        store_id_right_space = None
        store_id_left_right_space = None
        data_check = None
        address_id = None
        company_id = None
        try:
            company_id = insert_test_company()
            address_id = insert_test_address(-1, 1)
            store_id = insert_test_store(company_id, address_id)
            store_id_left_space = insert_test_store(company_id, address_id, phone_number = ' 555-867-5309')
            store_id_right_space = insert_test_store(company_id, address_id, phone_number = '555-867-5309 ')
            store_id_left_right_space = insert_test_store(company_id, address_id, phone_number = ' 555-867-5309 ')
            data_check = StandardSqlDataChecker(self.data_check_types[data_check_type_id]).run_data_check()
            data_check_from_db = self.get_data_check(data_check.data_check_id)
            self.assertTrue(data_check_from_db.bad_data_rows >= 3)
            self.assertTrue(self.check_entity_id_in_data_check_values(store_id_left_space, data_check_from_db.data_check_values))
            self.assertTrue(self.check_entity_id_in_data_check_values(store_id_right_space, data_check_from_db.data_check_values))
            self.assertTrue(self.check_entity_id_in_data_check_values(store_id_left_right_space, data_check_from_db.data_check_values))
            self.assertFalse(self.check_entity_id_in_data_check_values(store_id, data_check_from_db.data_check_values))
        except:
            raise
        finally:
            if store_id is not None:
                delete_test_store(store_id)
            if store_id_left_space is not None:
                delete_test_store(store_id_left_space)
            if store_id_right_space is not None:
                delete_test_store(store_id_right_space)
            if store_id_left_right_space is not None:
                delete_test_store(store_id_left_right_space)
            if address_id is not None:
                delete_test_address(address_id)
            if company_id is not None:
                delete_test_company(company_id)
            if data_check is not None:
                delete_test_data_check(data_check.data_check_id)



#####################################################################################################################
###############################################   Helper Methods  ###################################################
#####################################################################################################################

    def get_data_check(self, data_check_id):
        # get the data_check back from the db
        row = select_test_data_check(data_check_id)

        data_check = DataCheck.standard_init(row.data_check_id, row.data_check_type_id, row.check_done, row.bad_data_rows)

        # get the data_check_values
        rows = select_test_data_check_values(data_check_id)
        for row in rows:
            data_check.data_check_values.append(DataCheckValue.standard_init(row.data_check_value_id, row.data_check_id, row.value_type, row.expected_value, row.actual_value, row.entity_id))
        data_check.bad_data_rows = len(data_check.data_check_values)
        return data_check

    def check_entity_id_in_data_check_values(self, id, data_check_values):
        for data_check_value in data_check_values:
            if data_check_value.entity_id == id:
                return True
        return False

#####################################################################################################################
#####################################################   Main  #######################################################
#####################################################################################################################
if __name__ == "__main__":
    unittest.main()