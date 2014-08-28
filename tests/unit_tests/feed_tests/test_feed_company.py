from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from feed.helpers.feed_helper import date_YYYY_MM_DD
from feed.tables.entity.feed_company import FeedCompany
import datetime
import mox
import unittest

__author__ = 'jsternberg'

class FeedCompanyTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedCompanyTests, self).setUp()
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
        self.feed_company = FeedCompany(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_run(self):
        """
        Verify it calls the right funcs, yo
        """

        self.mox.StubOutWithMock(self.feed_company, "export_raw")
        self.mox.StubOutWithMock(self.feed_company, "get_export_row_count")
        self.mox.StubOutWithMock(self.feed_company, "get_industries_published_for_competition")
        self.mox.StubOutWithMock(self.feed_company, "make_final")
        self.mox.StubOutWithMock(self.feed_company, "get_final_row_count")
        self.mox.StubOutWithMock(self.feed_company, "validate_final_row_count_exact")

        mock_export_result = self.mox.CreateMockAnything()
        mock_export_result.succeeded = True
        self.feed_company.export_result = mock_export_result

        # record
        self.feed_company.export_raw()
        self.feed_company.get_export_row_count()
        self.feed_company.get_industries_published_for_competition()
        self.feed_company.make_final()
        self.feed_company.get_final_row_count()
        self.feed_company.validate_final_row_count_exact()

        # replay
        self.mox.ReplayAll()

        # test
        result = self.feed_company.run()

        expected_result = {
            "final_file": self.feed_company.final_file,
            "status": self.feed_company.status,
            "row_count_raw": self.feed_company.row_count_raw,
            "row_count_final": self.feed_company.row_count_final,
            "duration": self.feed_company.duration
        }

        self.assertEqual(result, expected_result)

    def test_write_clean_row__basic(self):
        """
        The most important function in the class. This tests the base case -- good / expected data.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_company.comp_published_industries = {u"52f83fc22345e32965167683"}

        analytics_date = date_YYYY_MM_DD(datetime.datetime.utcnow())
        created_date = date_YYYY_MM_DD(datetime.datetime.utcnow())
        modified_date = date_YYYY_MM_DD(datetime.datetime.utcnow())

        test_row = [
            u"ObjectID(123456789012)",  # company_id
            u"Spinal Tap",              # name
            u"hair_band",               # type
            u"old",                     # status
            None,                       # ticker
            u"None",                    # exchange
            u'[ { "entity_type_from" : "company", "entity_id_to" : { "$oid" : "52f83fc22345e32965167683" }, "interval" : null, "relation_type" : "industry_classification", "entity_role_from" : "primary_industry_classification", "entity_id_from" : { "$oid" : "528aca872345e319f955d446" }, "entity_type_to" : "industry", "_id" : { "$oid" : "52f97ddf2345e37fd721c7bf" }, "data" : { "properties" : { "primary" : true, "ownership" : false } }, "entity_role_to" : "primary_industry" } ]',
            u'''The band was started by childhood friends, David St. Hubbins (Michael McKean) and Nigel Tufnel (Christopher Guest), during the 1960s. Originally named "The Originals", then "The New Originals" to distinguish themselves from an existing group of the same name,[6] they settled on the name "The Thamesmen", finding success with their skiffle/rhythm and blues single "Gimme Some Money".
            They changed their name again to "Spinal Tap" and enjoyed limited success with the flower power anthem "Listen to the Flower People". Ultimately, the band became successful with heavy metal and produced several albums.
            The group was joined eventually by bassist Derek Smalls (Harry Shearer), keyboardist Viv Savage (David Kaff), and a series of drummers, each of whom mysteriously died in odd circumstances, including spontaneous human combustion, a "bizarre gardening accident" and, in at least one case, choking to death on the vomit of person(s) unknown.''',
            analytics_date,             # analytics.end_time
            created_date,               # created_at
            modified_date               # updated_at
        ]
        expected_clean_rows = [[
            u"123456789012",
            u"Spinal Tap",
            u"hair_band",
            u"old",
            u"",
            u"",
            u"52f83fc22345e32965167683",
            u'''The band was started by childhood friends, David St. Hubbins (Michael McKean) and Nigel Tufnel (Christopher Guest), during the 1960s. Originally named "The Originals", then "The New Originals" to distinguish themselves from an existing group of the same name,[6] they settled on the name "The Thamesmen", finding success with their skiffle/rhythm and blues single "Gimme Some Money".
            They changed their name again to "Spinal Tap" and enjoyed limited success with the flower power anthem "Listen to the Flower People". Ultimately, the band became successful with heavy metal and produced several albums.
            The group was joined eventually by bassist Derek Smalls (Harry Shearer), keyboardist Viv Savage (David Kaff), and a series of drummers, each of whom mysteriously died in odd circumstances, including spontaneous human combustion, a "bizarre gardening accident" and, in at least one case, choking to death on the vomit of person(s) unknown.''',
            analytics_date,
            u"1",
            created_date,
            modified_date
        ]]

        self.feed_company._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)


    def __mock_write_row(self, values):
        self.row_values.append(values)


if __name__ == '__main__':
    unittest.main()
