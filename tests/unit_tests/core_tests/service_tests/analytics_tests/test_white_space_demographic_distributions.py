import mox
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.business_logic.service_entity_logic import white_space_grid_helper
from core.service.svc_analytics.implementation.calc.calc_engine import CalcEngine
from core.service.svc_analytics.implementation.calc.engines.demographics.white_space_demographic_distributions import WhiteSpaceDemographicDistributions
from scipy import stats
from bson import ObjectId

__author__ = 'erezrubinstein'

class StoreCountTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(StoreCountTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get some mock providers
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock_logger = Dependency("FlaskLogger").value

        # blah!!!
        self.maxDiff = None

        # create base calc
        self.context = {"user_id": 1, "source": "here" }
        self.banner_ids = ["chicken", "woot"]
        self.run_params = { "target_entity_ids": self.banner_ids }
        self.calc = WhiteSpaceDemographicDistributions(None, self.mock_logger, None, None, None, None, None, self.run_params, self.context)

        # set up common vars in the base calc
        self.calc.thresholds = ["threshold_1", "threshold_2"]

        # since we switched to the new JSON ecoder/decoder, we need to deal with bson ObjectId's
        self.cell_id1 = ObjectId()
        self.cell_id2 = ObjectId()
        self.cell_id3 = ObjectId()
        self.cell_id11 = ObjectId()
        self.cell_id12 = ObjectId()

    def doCleanups(self):

        super(StoreCountTests, self).doCleanups()
        dependencies.clear()

    def test_calculate__no_competition(self):

        # create a bunch of mock matches for the two companies for the 2 thresholds
        # make a few of them have openings, but not all
        mock_matches = [
            # match_id, cell_id, store_count, has_openings, threshold, company_id
            ["id", self.cell_id1, 1, True, "threshold_1", "chicken"],
            ["id", self.cell_id2, 2, True, "threshold_1", "chicken"],
            ["id", self.cell_id11, 11, True, "threshold_2", "chicken"],
            ["id", self.cell_id12, 12, True, "threshold_2", "chicken"],
            ["id", self.cell_id1, 1, False, "threshold_1", "woot"],
            ["id", self.cell_id2, 2, False, "threshold_1", "woot"],
            ["id", self.cell_id11, 11, True, "threshold_2", "woot"],
            ["id", self.cell_id12, 12, True, "threshold_2", "woot"]
        ]

        # mock the cells and demographics
        mock_cells = [
            self._create_mock_cell(self.cell_id1),
            self._create_mock_cell(self.cell_id2),
            self._create_mock_cell(self.cell_id11),
            self._create_mock_cell(self.cell_id12)
        ]

        # set mocks
        self.calc.fetched_data = mock_matches
        self.calc.cells = mock_cells
        self.calc.competition = {}
        self.calc.competitive_matches = {}

        # run baby, run!
        self.calc._calculate()

        # create expected results
        expected_results = {
            "chicken": {
                "threshold_1": {
                    "current": self._round_numbers(self._create_expected_results(1, 2)),
                    "openings": self._round_numbers(self._create_expected_results(1, 2))
                },
                "threshold_2": {
                    "current": self._round_numbers(self._create_expected_results(11, 12)),
                    "openings": self._round_numbers(self._create_expected_results(11, 12))
                }
            },
            "woot": {
                "threshold_1": {
                    "current": self._round_numbers(self._create_expected_results(1, 2)),
                    "openings": self._round_numbers(self._create_expected_results(None, None))
                },
                "threshold_2": {
                    "current": self._round_numbers(self._create_expected_results(11, 12)),
                    "openings": self._round_numbers(self._create_expected_results(11, 12))
                }
            }
        }

        # round both sets so that they match
        self.calc.results["chicken"]["threshold_1"]["current"] = self._round_numbers(self.calc.results["chicken"]["threshold_1"]["current"])
        self.calc.results["chicken"]["threshold_1"]["openings"] = self._round_numbers(self.calc.results["chicken"]["threshold_1"]["openings"])
        self.calc.results["chicken"]["threshold_2"]["current"] = self._round_numbers(self.calc.results["chicken"]["threshold_2"]["current"])
        self.calc.results["chicken"]["threshold_2"]["openings"] = self._round_numbers(self.calc.results["chicken"]["threshold_2"]["openings"])
        self.calc.results["woot"]["threshold_1"]["current"] = self._round_numbers(self.calc.results["woot"]["threshold_1"]["current"])
        self.calc.results["woot"]["threshold_1"]["openings"] = self._round_numbers(self.calc.results["woot"]["threshold_1"]["openings"])
        self.calc.results["woot"]["threshold_2"]["current"] = self._round_numbers(self.calc.results["woot"]["threshold_2"]["current"])
        self.calc.results["woot"]["threshold_2"]["openings"] = self._round_numbers(self.calc.results["woot"]["threshold_2"]["openings"])

        self.assertEquals(self.calc.results, expected_results)


    def test_calculate__with_competition__one_demographic__one_threshold(self):

        # create a bunch of mock matches for the two companies for the 2 thresholds
        # make a few of them have openings, but not all
        mock_matches = [
            # match_id, cell_id, store_count, has_openings, threshold, company_id
            ["id", self.cell_id1, 1, True, "threshold_1", "chicken"],
            ["id", self.cell_id2, 2, True, "threshold_1", "chicken"]
        ]

        # mock the cells and demographics
        mock_cells = [
            self._create_mock_cell(self.cell_id1),
            self._create_mock_cell(self.cell_id2)
        ]

        # create mock competition
        mock_competition = {
            "chicken": 1,
            "chilly": 1,
            "willy": .5
        }

        # create mock competition matches for three cells.  Fourth is a cannibalized monopoly.
        mock_competition_matches = {
            str(self.cell_id1): [
                { "data": { "store_count": 3, "company_id": "chilly" }},
                { "data": { "store_count": 4, "company_id": "willy" }}
            ],
            str(self.cell_id2): [
                { "data": { "store_count": 5, "company_id": "chilly" }},
                { "data": { "store_count": 6, "company_id": "willy" }}
            ]
        }

        # set mocks
        self.calc.run_params = { "target_entity_ids": ["chicken"] }
        self.calc.thresholds = ["threshold_1"]
        self.calc.demographics = ["FEMALES_CY"]
        self.calc.fetched_data = mock_matches
        self.calc.cells = mock_cells
        self.calc.competition = mock_competition
        self.calc.competitive_matches = mock_competition_matches

        # run baby, run!
        self.calc._calculate()

        # create expected results
        expected_results = {
            "chicken": {
                "threshold_1": {
                    "current": self._round_numbers({ "FEMALES_CY": self._get_distribution_assuming_2_cells(120, 1, 2, 6, 10) }),
                    "openings": self._round_numbers({ "FEMALES_CY": self._get_distribution_assuming_2_cells(120, 1, 2, 6, 10) })
                }
            }
        }

        # round both sets so that they match
        self.calc.results["chicken"]["threshold_1"]["current"] = self._round_numbers(self.calc.results["chicken"]["threshold_1"]["current"])
        self.calc.results["chicken"]["threshold_1"]["openings"] = self._round_numbers(self.calc.results["chicken"]["threshold_1"]["openings"])

        self.assertEquals(self.calc.results, expected_results)


    def test_fetch(self):

        # mock vars
        mock_matches = [
            # match_id, cell_id, store_count, has_openings, threshold, company_id
            ["id", self.cell_id1, 1, True, "threshold_1", "chicken"],
            ["id", self.cell_id2, 2, True, "threshold_1", "chicken"]
        ]
        mock_cell_ids = [self.cell_id1, self.cell_id2]
        mock_thresholds = [
            { "data": { "threshold": "chilly" }},
            { "data": { "threshold": "willy" }}
        ]

        # mock calc
        self.calc.run_params["demographics"] = ["falafel"]
        self.calc.input = {}

        # consequences
        def fetch_side_effects():
            self.calc.fetched_data = mock_matches

        # stub out stuff
        self.mox.StubOutWithMock(CalcEngine, "_fetch")
        self.mox.StubOutWithMock(self.calc, "_fetch_cells_with_demographics")
        self.mox.StubOutWithMock(self.calc, "_fetch_competitive_matches")
        self.mox.StubOutWithMock(white_space_grid_helper, "select_grid_thresholds")

        # begin recording
        white_space_grid_helper.select_grid_thresholds().AndReturn(mock_thresholds)
        CalcEngine._fetch().WithSideEffects(fetch_side_effects)
        self.calc._fetch_cells_with_demographics(mock_cell_ids).AndReturn("woot")
        self.calc._fetch_competitive_matches(mock_cell_ids).AndReturn("chicken")

        # replay all
        self.mox.ReplayAll()

        # make sure the bellow is backwards compatible
        self.calc._fetch()

        # verify that all the things in calc are set up correctly
        self.assertEqual(self.calc.competition, {})
        self.assertEqual(self.calc.cells, "woot")
        self.assertEqual(self.calc.competitive_matches, "chicken")
        self.assertEqual(self.calc.thresholds, ["chilly", "willy"])
        self.assertEqual(self.calc.demographics, ["falafel"])
        self.assertEqual(self.calc.input["entity_query"], { "data.threshold": { "$in": ["chilly", "willy"] }})


    def test_fetch_competitive_matches(self):

        # mocks
        mock_target_cell_ids = map(str, [self.cell_id1, self.cell_id2, self.cell_id3])
        mock_competition = {
            "woot": 1,
            "chicken": 2,
            "chilly": 2,
            "willy": 5
        }
        mock_params = {
            "entity_fields": ["_id", "data.cell_id", "data.store_count", "data.company_id"],
            "query": {
                "data.cell_id": { "$in": mock_target_cell_ids },

                # important! we don't query chicken or woot, because they're targets and we already have their matches
                "data.company_id": { "$in": ["willy", "chilly"] }
            }
        }
        mock_competitive_matches = [
            { "data": { "cell_id": self.cell_id1, "store_count": 1 }},
            { "data": { "cell_id": self.cell_id1, "store_count": 2 }},
            { "data": { "cell_id": self.cell_id2, "store_count": 3 }},
            { "data": { "cell_id": self.cell_id2, "store_count": 4 }},
            { "data": { "cell_id": self.cell_id3, "store_count": 5 }},
        ]

        # set up mocks
        self.calc.competition = mock_competition

        # begin recording
        self.mock_main_access.mds.call_find_entities_raw("white_space_grid_cell_match", mock_params, self.context, encode_and_decode_results=False).AndReturn(mock_competitive_matches)

        # replay all
        self.mox.ReplayAll()

        # go, sucka!
        competitive_matches = self.calc._fetch_competitive_matches(mock_target_cell_ids)

        # verify that the competitive_matches are in the correct structure
        self.assertEqual(competitive_matches, {
            self.cell_id1: [
                { "data": { "cell_id": self.cell_id1, "store_count": 1 }},
                { "data": { "cell_id": self.cell_id1, "store_count": 2 }}
            ],
            self.cell_id2: [
                { "data": { "cell_id": self.cell_id2, "store_count": 3 }},
                { "data": { "cell_id": self.cell_id2, "store_count": 4 }}
            ],
            self.cell_id3: [
                { "data": { "cell_id": self.cell_id3, "store_count": 5 }}
            ]
        })


    # ----------------------------------- Private Helpers ----------------------------------- #

    def _round_numbers(self, distributions):
        """
        rounding differences in scipy versus my distribution
        """

        rounded = {}

        for dem in distributions:
            rounded[dem] = []
            for number in distributions[dem]:
                rounded[dem].append(round(float(number), 5))

        return rounded

    def _create_mock_cell(self, id):

        return {
            "_id": id,
            "data": {
                "demographics": {
                    "TOTPOP_CY": { "value": 10 },
                    "TOTHH_CY": { "value": 20 },
                    "HINC0_CY": { "value": 30 },
                    "HINC15_CY": { "value": 40 },
                    "HINC25_CY": { "value": 50 },
                    "HINC35_CY": { "value": 60 },
                    "HINC50_CY": { "value": 70 },
                    "HINC75_CY": { "value": 80 },
                    "HINC100_CY": { "value": 90 },
                    "HINC150_CY": { "value": 100 },
                    "HINC200_CY": { "value": 110 },
                    "FEMALES_CY": { "value": 120 },
                    "FEMALE_15PLUS": { "value": 130 },
                    "HINC_100KPLUS": { "value": 140 },
                    "HINC_35KTO75K": { "value": 150 },
                    "HINC_50KPLUS_CY": { "value": 160 },
                    "HINC_LESSTHAN35K": { "value": 170 },
                    "HINC_LESSTHAN50K": { "value": 180 },
                    "MALES_CY": { "value": 190 },
                    "MEDHINC_CY": { "value": 200 },
                    "PCI_CY": { "value": 210 },
                    "TOTHH_FY": { "value": 220 },
                    "TOTPOP_FY": { "value": 230 }
                },
                "analytics": {
                    "AGG_INCOME_CY": { "value": 120 }
                }
            }
        }

    def _create_expected_results(self, cell_1_stores, cell_2_stores, cell_1_weighted_store_count = None, cell_2_weighted_store_count = None):

        if not cell_1_weighted_store_count:
            cell_1_weighted_store_count = cell_1_stores

        if not cell_2_weighted_store_count:
            cell_2_weighted_store_count = cell_2_stores

        return {
            "TOTPOP_CY": self._get_distribution_assuming_2_cells(10, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "TOTHH_CY": self._get_distribution_assuming_2_cells(20, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC0_CY": self._get_distribution_assuming_2_cells(30, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC15_CY": self._get_distribution_assuming_2_cells(40, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC25_CY": self._get_distribution_assuming_2_cells(50, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC35_CY": self._get_distribution_assuming_2_cells(60, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC50_CY": self._get_distribution_assuming_2_cells(70, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC75_CY": self._get_distribution_assuming_2_cells(80, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC100_CY": self._get_distribution_assuming_2_cells(90, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC150_CY": self._get_distribution_assuming_2_cells(100, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC200_CY": self._get_distribution_assuming_2_cells(110, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "AGG_INCOME_CY": self._get_distribution_assuming_2_cells(120, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "FEMALES_CY": self._get_distribution_assuming_2_cells(120, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "FEMALE_15PLUS": self._get_distribution_assuming_2_cells(130, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC_100KPLUS": self._get_distribution_assuming_2_cells(140, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC_35KTO75K": self._get_distribution_assuming_2_cells(150, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC_50KPLUS_CY": self._get_distribution_assuming_2_cells(160, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC_LESSTHAN35K": self._get_distribution_assuming_2_cells(170, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "HINC_LESSTHAN50K": self._get_distribution_assuming_2_cells(180, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "MALES_CY": self._get_distribution_assuming_2_cells(190, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "MEDHINC_CY": self._get_distribution_assuming_2_cells(200, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "PCI_CY": self._get_distribution_assuming_2_cells(210, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "TOTHH_FY": self._get_distribution_assuming_2_cells(220, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count),
            "TOTPOP_FY": self._get_distribution_assuming_2_cells(230, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count)
        }

    def _get_distribution_assuming_2_cells(self, dem_value, cell_1_stores, cell_2_stores, cell_1_weighted_store_count, cell_2_weighted_store_count):

        # for no stores....
        if not cell_1_stores and not cell_2_stores:
            return []

        # start with an empty list
        values = []

        # add all cell_1 values to the list
        for i in range(0, cell_1_stores):
            values.append(dem_value / float(cell_1_weighted_store_count))

        # add all cell_2 values to the list
        for i in range(0, cell_2_stores):
            values.append(dem_value / float(cell_2_weighted_store_count))

        return [
            stats.scoreatpercentile(values, 10),
            stats.scoreatpercentile(values, 20),
            stats.scoreatpercentile(values, 30),
            stats.scoreatpercentile(values, 40),
            stats.scoreatpercentile(values, 50),
            stats.scoreatpercentile(values, 60),
            stats.scoreatpercentile(values, 70),
            stats.scoreatpercentile(values, 80),
            stats.scoreatpercentile(values, 90),
            stats.scoreatpercentile(values, 100)
        ]
