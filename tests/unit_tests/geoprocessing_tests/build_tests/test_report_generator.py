import unittest
from datetime import datetime
from geoprocessing.build.report_generator import ReportGenerator
from geoprocessing.business_logic.business_objects.address import Address
from geoprocessing.business_logic.business_objects.company import Company
from geoprocessing.business_logic.business_objects.data_check import DataCheckType
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockRowCount, MockLogFunctionPerformance, MockNonSqlDataRowCount
from common.utilities.Logging.sql_logging_handler import LogEntryType, LogEntry


class ReportGeneratorTests(unittest.TestCase):
    def setUp(self):
        register_mock_dependencies()
        self._email_provider = Dependency("EmailProvider").value
        self._config = Dependency("Config").value
        self._data_provider = Dependency("DataRepository").value
        self._file_provider = Dependency("FileProvider").value
        self._deployment_provider = Dependency("DeploymentProvider").value

    def tearDown(self):
        dependencies.clear()

    def test_report_generator_row_counts(self):
        self._deployment_provider.s3_files.clear()
        self._file_provider.files.clear()

        #TODO: finish test, trade area
        # mock config table names
        self._config.report_generator_table_names = ['companies', 'monarchs']
        self._data_provider.table_row_counts['companies'] = MockRowCount('companies', 5)
        self._data_provider.table_row_counts['monarchs'] = MockRowCount('monarchs', 15)

        # mock log entries
        self._data_provider.logs_by_log_entry_type_id[LogEntryType.CRITICAL] = []
        self._data_provider.logs_by_log_entry_type_id[LogEntryType.ERROR] = []
        self._data_provider.logs_by_log_entry_type_id[LogEntryType.CRITICAL].append(LogEntry(1, "version", "environment", "process", str(datetime.utcnow()), "unit test message critical", "class_func1", None, entity = None))
        self._data_provider.logs_by_log_entry_type_id[LogEntryType.ERROR].append(LogEntry(2, "version", "environment", "process", str(datetime.utcnow()), "unit test message error", "class_func2", None, entity = None))

        # mock function performance log entries
        self._data_provider.function_performance_logs.append(MockLogFunctionPerformance('hasta_la_vista_baby', 999, 123))
        self._data_provider.function_performance_logs.append(MockLogFunctionPerformance('become_self_aware', 999999, 1))

        # mock data check types
        data_check_type_address = DataCheckType.standard_init(-1, 'data check address', 1, 'select judgement_date from skynet', 9, 0)
        data_check_type_store = DataCheckType.standard_init(-2, 'data check store', 2, 'select judgement_date from skynet', 9, 0)
        data_check_type_company = DataCheckType.standard_init(-3, 'data check company', 3, 'select judgement_date from skynet', 9, 0)
        data_check_type_trade_area = DataCheckType.standard_init(-4, 'data check trade area', 4, 'select judgement_date from skynet', 9, 0)
        self._data_provider.data_check_types[data_check_type_address.data_check_type_id] = data_check_type_address
        self._data_provider.data_check_types[data_check_type_store.data_check_type_id] = data_check_type_store
        self._data_provider.data_check_types[data_check_type_company.data_check_type_id] = data_check_type_company
        #self._data_provider.data_check_types[data_check_type_trade_area.data_check_type_id] = data_check_type_trade_area

        # mock data check sql execute results
        self._data_provider.data_check_entity_ids[data_check_type_address] = [[-1], [-2], [-3]]
        self._data_provider.data_check_entity_ids[data_check_type_store] = [[-1]]
        self._data_provider.data_check_entity_ids[data_check_type_company] = [[-2]]
        #self._data_provider.data_check_entity_ids[data_check_type_trade_area] = [[-3]]

        # mock addresses for id's above in data_check_entity_ids
        self._data_provider.addresses[-1] = Address.standard_init(-1, 11, 'blah st', 'asdf', 'AA', '13243-2341', 840, -1, 1, '123', 'asdlfkj')
        self._data_provider.addresses[-2] = Address.standard_init(-2, 11, 'dfsa st', 'dfsse', 'BB', '29341-3241', 840, -1, 1, '45', 'fseex')
        self._data_provider.addresses[-3] = Address.standard_init(-3, 11, 'gaseax st', 'w3sad', 'CC', '90873-9832', 840, -1, 1, '2', 'fasdfasdf')

        # mock stores
        self._data_provider.stores[-1] = Store.standard_init(-1, -2, -1, '555-555-5555', None, None, None, datetime.now(), datetime.now(), datetime.now(), datetime.now())

        # mock company
        self._data_provider.companies[-2] = Company.standard_init(-2, 'asdf', 'skynet', datetime.now(), datetime.now())

#        # mock trade area
#        mock_trade_area = TradeArea()
#        mock_trade_area.trade_area_id = -3
#        mock_trade_area.store_id = -1
#        mock_trade_area.threshold_id = -4
#        mock_trade_area.period_id = -3
#        mock_trade_area.area = None
#        self._data_provider.mock_trade_areas[-3] = mock_trade_area

        # mock non sql data check rowcounts
        self._data_provider.non_sql_data_check_rowcounts.append(MockNonSqlDataRowCount('ReverseGeocodeESRI', 20))
        self._data_provider.non_sql_data_check_rowcounts.append(MockNonSqlDataRowCount('ReverseGeocodeGoogle', 10))

        ReportGenerator().generate_reports()

        # test the email
        email = self._email_provider.html_message
        self.assertIn('Environment', email)
        self.assertIn('Config Filename', email)
        self.assertIn('Server', email)
        self.assertIn('Build Elapsed Time', email)

        # test the file
        # pop the first item off the files dictionary
        full_filename, file = self._file_provider.files.popitem()
        self.assertIn('hasta_la_vista_baby', file)
        self.assertIn('data check address', file)
        self.assertIn('gaseax st', file)
        self.assertIn('-3', file)
        self.assertIn('unit test message critical', file)
        self.assertIn('123', file)
        self.assertIn('ReverseGeocodeESRI', file)
        self.assertIn('ReverseGeocodeGoogle', file)

        # test s3 upload
        # verify s3cmd params
#        self.assertEqual(self._deployment_provider.s3_config_files[0], join(getenv("HOME"), ".s3cfg"))
        self.assertEqual(self._deployment_provider.s3_directories[0], "s3://signal-reports/")
        self.assertIn(full_filename, self._deployment_provider.s3_files[self._config.report_generator_s3_report_directory])



if __name__ == '__main__':
    unittest.main()
