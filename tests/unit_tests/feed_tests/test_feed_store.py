from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from feed.helpers.feed_helper import date_YYYY_MM_DD
from feed.tables.entity.feed_store import FeedStore
import datetime
import mox
import unittest

__author__ = 'jsternberg'

class FeedStoreTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedStoreTests, self).setUp()
        # set up mocks
        register_common_mock_dependencies()

        mock_config = {
            "MONGODB_HOST_MDS": "nope",
            "MONGODB_PORT_MDS": "no_way",
            "DB_PREFIX": "you_wish",
            "FEED_OUTPUT_DIR": "most_certainly_not",
            "FEED_REPORTS_BATCH_DIR": "nadda"
        }
        mock_logger = Dependency("SimpleConsole").value
        self.feed_store = FeedStore(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_run(self):
        """
        Verify it calls the right funcs, yo
        """

        self.mox.StubOutWithMock(self.feed_store, "export_raw")
        self.mox.StubOutWithMock(self.feed_store, "get_export_row_count")
        self.mox.StubOutWithMock(self.feed_store, "get_company_ids_from_company_file")
        self.mox.StubOutWithMock(self.feed_store, "get_address_ids_from_address_file")
        self.mox.StubOutWithMock(self.feed_store, "make_final")
        self.mox.StubOutWithMock(self.feed_store, "get_final_row_count")
        self.mox.StubOutWithMock(self.feed_store, "validate_final_row_count_within_tolerance")
        self.mox.StubOutWithMock(self.feed_store, "get_address_ids_from_store_file")
        self.mox.StubOutWithMock(self.feed_store, "get_row_count_of_file")
        self.mox.StubOutWithMock(self.feed_store, "remove_unlinked_addresses")
        self.mox.StubOutWithMock(self.feed_store, "validate_counter_vs_counter")

        mock_export_result = self.mox.CreateMockAnything()
        mock_export_result.succeeded = True
        self.feed_store.export_result = mock_export_result

        # record
        self.feed_store.export_raw()
        self.feed_store.get_export_row_count()
        self.feed_store.get_company_ids_from_company_file()
        self.feed_store.get_address_ids_from_address_file()
        self.feed_store.make_final()
        self.feed_store.get_final_row_count()
        self.feed_store.validate_final_row_count_within_tolerance(tolerance=0.20)
        self.feed_store.get_address_ids_from_store_file()
        self.feed_store.get_row_count_of_file(self.feed_store.address_file).AndReturn(100)
        self.feed_store.remove_unlinked_addresses()
        self.feed_store.get_row_count_of_file(self.feed_store.address_file).AndReturn(100)
        self.feed_store.validate_counter_vs_counter("address table after unlinking",
                                                    100,
                                                    "address table before unlinking minus number of unlinked addresses",
                                                    100)

        # replay
        self.mox.ReplayAll()

        # test
        result = self.feed_store.run()

        expected_result = {
            "final_file": self.feed_store.final_file,
            "status": self.feed_store.status,
            "row_count_raw": self.feed_store.row_count_raw,
            "row_count_final": self.feed_store.row_count_final,
            "num_unlinked_addresses": self.feed_store.num_unlinked_addresses,
            "num_stores_null_company_id": self.feed_store.num_stores_null_company_id,
            "num_stores_null_address_id": self.feed_store.num_stores_null_address_id,
            "num_stores_linked_to_non_feed_company": self.feed_store.num_stores_linked_to_non_feed_company,
            "num_stores_linked_to_missing_address": self.feed_store.num_stores_linked_to_missing_address,
            "stores_null_company_id_report": self.feed_store.stores_null_company_id_report,
            "stores_null_address_id_report": self.feed_store.stores_null_address_id_report,
            "stores_linked_to_non_feed_company_report": self.feed_store.stores_linked_to_non_feed_company_report,
            "stores_linked_to_missing_address_report": self.feed_store.stores_linked_to_missing_address_report,
            "duration": self.feed_store.duration
        }

        self.assertEqual(result, expected_result)

    def test_write_clean_row__basic(self):
        """
        The most important function in the class. This tests the base case -- good / expected data.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_store.company_ids_in_feed = {u"51f791d53f0cd2795ffd4b43"}
        self.feed_store.address_ids_in_feed = {u"52809c9c3f0cd20ede6741fb"}

        open_date = date_YYYY_MM_DD(datetime.datetime.utcnow())
        close_date = date_YYYY_MM_DD(datetime.datetime.utcnow())
        created_date = date_YYYY_MM_DD(datetime.datetime.utcnow())
        modified_date = date_YYYY_MM_DD(datetime.datetime.utcnow())

        test_row = [
            u"ObjectID(52809c9c3f0cd20ede6741fc)",      # store_id
            u'[ { "entity_type_from" : "store", "entity_id_to" : { "$oid" : "51f791d53f0cd2795ffd4b43" }, "interval" : null, "relation_type" : "store_ownership", "entity_role_from" : "store", "entity_id_from" : { "$oid" : "52809c9c3f0cd20ede6741fc" }, "entity_type_to" : "company", "_id" : { "$oid" : "52809cad3f0cd27641853221" }, "data" : { "properties" : { "ownership" : false } }, "entity_role_to" : "retail_parent" } ]',
            u'[ { "entity_type_from" : "store", "entity_id_to" : { "$oid" : "52809c9c3f0cd20ede6741fb" }, "interval" : null, "relation_type" : "address_assignment", "entity_role_from" : "subject", "entity_id_from" : { "$oid" : "52809c9c3f0cd20ede6741fc" }, "entity_type_to" : "address", "_id" : { "$oid" : "52809c9c3f0cd20ede674202" }, "data" : { "properties" : { "ownership" : false } }, "entity_role_to" : "location" } ]',
            open_date,                                  # open_date
            close_date,                                 # close_date
            u"5551212",                                 # phone
            u"7B",                                      # store_number
            u"So I says to Mabel I says",               # note
            u"really, really great",                    # store_format
            created_date,                               # created_at
            modified_date                               # modified_at
        ]
        expected_clean_rows = [[
            u"52809c9c3f0cd20ede6741fc",
            u"51f791d53f0cd2795ffd4b43",
            u"52809c9c3f0cd20ede6741fb",
            open_date,
            close_date,
            u"5551212",
            u"7B",
            u"So I says to Mabel I says",
            u"really, really great",
            created_date,
            modified_date
        ]]

        self.feed_store._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)


    def __mock_write_row(self, values):
        self.row_values.append(values)


if __name__ == '__main__':
    unittest.main()
