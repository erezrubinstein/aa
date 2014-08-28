from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from feed.helpers.feed_helper import date_YYYY_MM_DD
from feed.tables.entity.feed_company_relationship import FeedCompanyRelationship
from bson import ObjectId
import datetime
import mox
import unittest

__author__ = 'jsternberg'

class FeedCompanyRelationshipTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedCompanyRelationshipTests, self).setUp()
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
        self.feed_company_relationship = FeedCompanyRelationship(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_run(self):
        """
        Verify it calls the right funcs, yo
        """

        self.mox.StubOutWithMock(self.feed_company_relationship, "export_raw")
        self.mox.StubOutWithMock(self.feed_company_relationship, "get_export_row_count")
        self.mox.StubOutWithMock(self.feed_company_relationship, "get_company_ids_from_company_file")
        self.mox.StubOutWithMock(self.feed_company_relationship, "make_final")
        self.mox.StubOutWithMock(self.feed_company_relationship, "get_final_row_count")
        self.mox.StubOutWithMock(self.feed_company_relationship, "validate_final_row_count_vs_counter")

        mock_export_result = self.mox.CreateMockAnything()
        mock_export_result.succeeded = True
        self.feed_company_relationship.export_result = mock_export_result

        # record
        self.feed_company_relationship.export_raw()
        self.feed_company_relationship.get_export_row_count()
        self.feed_company_relationship.get_company_ids_from_company_file()
        self.feed_company_relationship.make_final()
        self.feed_company_relationship.get_final_row_count()
        self.feed_company_relationship.validate_final_row_count_vs_counter(1)

        # replay
        self.mox.ReplayAll()

        # test
        result = self.feed_company_relationship.run()

        expected_result = {
            "final_file": self.feed_company_relationship.final_file,
            "status": self.feed_company_relationship.status,
            "row_count_raw": self.feed_company_relationship.row_count_raw,
            "row_count_final": self.feed_company_relationship.row_count_final,
            "num_links_from_non_feed_company": self.feed_company_relationship.num_links_from_non_feed_company,
            "num_links_to_non_feed_company": self.feed_company_relationship.num_links_to_non_feed_company,
            "links_from_non_feed_company_report": self.feed_company_relationship.links_from_non_feed_company_report,
            "links_to_non_feed_company_report": self.feed_company_relationship.links_to_non_feed_company_report,
            "duration": self.feed_company_relationship.duration
        }

        self.assertEqual(result, expected_result)

    def test_write_clean_row__basic(self):
        """
        The most important function in the class. This tests the base case -- good / expected data.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_company_relationship.company_ids_in_feed = {
            u"5208597927eb40540c821f06", u"5285d1612345e36592772608", u"5285d1612345e36592772609"
        }

        test_row = [
            # retailer_branding
            u'''[{
                "entity_type_from" : "company",
                "entity_id_to" : {
                        "$oid": "5285d1612345e36592772608"
                },
                "interval": [
                    {
                      "$date": 1321315200000
                    },
                    {
                      "$date": 1479168000000
                    }
                ],
                "relation_type": "retailer_branding",
                "entity_role_from": "retail_segment",
                "entity_id_from": {
                    "$oid": "5208597927eb40540c821f06"
                },
                "entity_type_to": "company",
                "_id": {
                    "$oid": "52c50db62345e37a6884d1f6"
                },
                "data": {
                    "properties": {
                        "ownership": false
                    }
                },
                "entity_role_to": "retail_parent"
            }]''',
            # retailer_cooperatives
            u'''[{
                "entity_type_from" : "company",
                "entity_id_to" : {
                        "$oid": "5285d1612345e36592772609"
                },
                "interval": [
                    {
                      "$date": 1321315200000
                    },
                    {
                      "$date": 1479168000000
                    }
                ],
                "relation_type": "retailer_cooperatives",
                "entity_role_from": "retail_segment",
                "entity_id_from": {
                    "$oid": "5208597927eb40540c821f06"
                },
                "entity_type_to": "company",
                "_id": {
                    "$oid": "52c50db62345e37a6884d1f6"
                },
                "data": {
                    "properties": {
                        "ownership": false
                    }
                },
                "entity_role_to": "retail_parent"
            }]''',
            # equity_investment
            u'',
            # private_investment
            u''
        ]

        created_date = modified_date = date_YYYY_MM_DD(ObjectId(u"52c50db62345e37a6884d1f6").generation_time)

        expected_clean_rows = [
            [
                u"retailer_branding",
                u"5208597927eb40540c821f06",
                u"retail_segment",
                u"5285d1612345e36592772608",
                u"retail_parent",
                created_date,
                modified_date
            ],
            [
                u"retailer_cooperatives",
                u"5208597927eb40540c821f06",
                u"retail_segment",
                u"5285d1612345e36592772609",
                u"retail_parent",
                created_date,
                modified_date
            ]
        ]

        self.feed_company_relationship._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)


    def __mock_write_row(self, values):
        self.row_values.append(values)


if __name__ == '__main__':
    unittest.main()
