from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.helpers.mock_providers.mock_mongodb_provider import MockMongoDBProvider
from common.utilities.Logging.simple_console_logger import SimpleConsoleLogger
from common.utilities.inversion_of_control import dependencies
import mox
import unittest
from core.service.svc_entity_matcher.implementation.train.pairs_for_training import PairGetter

__author__ = 'clairseager'


class MatcherTrainerTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(MatcherTrainerTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)
        self.logger = SimpleConsoleLogger()
        self.db = MockMongoDBProvider()
        self.db.db_names.append("prod_mds")

    def doCleanups(self):

        super(MatcherTrainerTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################

    def test__entity_to_record(self):
        rir = {
          "_id": "518344164af885655a9ab3a4",
          "data": {
            "auto_parsed_address": {
              "city": "Louisville",
              "zip": "40207",
              "street_number": "1805",
              "country": None,
              "longitude": -85.638201,
              "state": "KY",
              "street": "Rudy Lane",
              "latitude": 38.279013,
              "suite": None,
              "geo": [
                -85.638201,
                38.279013
              ],
              "shopping_center": None
            },
            "city": "Louisville",
            "zip": "40207",
            "company_id": "5183438e4af885658b91ba33",
            "state": "KY",
            "company_name": "The Fresh Market",
            "suite": None,
            "store_number": None,
            "workflow": {
              "retail_curation": {
                "input_sourcing": {
                  "churn_validation": {
                    "rirLinkID": "518343fb4af885655d304428",
                    "asOfDate": "2013-03-18",
                    "decision": "link",
                    "companyID": "5183438e4af885658b91ba33",
                    "rirID": "518344164af885655a9ab3a4",
                    "dataToUse": "existing",
                    "breakRIRChain": None,
                    "breakBeforeId": None,
                    "store_id": "518343fb4af885655d30442a"
                  }
                }
              }
            },
            "phone": "502.895.7593",
            "address": "1805 Rudy Lane",
            "geo": [
              "-85.638201",
              "38.279013"
            ],
            "country": None
          },
          "rirlinks": {
            "entity_type_from": "retail_input_record",
            "entity_id_to": "518343fb4af885655d304428",
            "interval": None,
            "relation_type": "retail_input",
            "entity_role_from": "target",
            "entity_id_from": "518344164af885655a9ab3a4",
            "entity_type_to": "retail_input_record",
            "_id": "51873a624af8857893191594",
            "data": {
              "category": "inexact",
              "match_type": "inexact",
              "timestamp": "2013-05-06T05:06:42.224000",
              "reason": {
                "diff_vals": {
                  "city": 1,
                  "zip": 1,
                  "street_number": 1,
                  "phone": 1,
                  "state": 1,
                  "street": 1,
                  "address": 1000
                }
              },
              "score": 1,
              "target_rir_id": "518344164af885655a9ab3a4",
              "matcher_prediction": "match",
              "potential_match_rir_id": "518343fb4af885655d304428",
              "properties": {
                "ownership": False
              }
            },
            "entity_role_to": "potential_match"
          },
        "link_chosen": True
        }

        rec = PairGetter.__new__(PairGetter)._entity_to_record(rir)

        expected = {
            'city': 'Louisville',
            'potential_match': '518343fb4af885655d304428',
            'zip': '40207',
            'street_number': '1805',
            'country': None,
            'longitude': -85.638201,
            'phone': '502.895.7593',
            'state': 'KY',
            'street': 'Rudy Lane',
            'human_decision': 'link',
            'address': {'city': 'Louisville', 'state': 'KY', 'zip': '40207', 'street_address': '1805 Rudy Lane'},
            'latitude': 38.279013,
            'suite': None,
            'id': '518344164af885655a9ab3a4',
            'shopping_center': None
        }


        self.assertDictEqual(expected, rec)



if __name__ == "__main__":
    unittest.main()