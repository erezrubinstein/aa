from core.service.svc_workflow.implementation.task.implementation.economics_tasks.national_labor_calculator import NationalLaborCalculator
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from bson.objectid import ObjectId
from pymongo import mongo_client


__author__ = "vgold"


class WFSNationalLaborCalculatorTestCollection(ServiceTestCollection):

    def initialize(self):

        # get params builder
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        # context
        self._context = {
            "user_id": ObjectId(),
            "source": "wfs_national_labor_calculator_test_collection.py"
        }

    def setUp(self):

        self.mds_access.call_delete_reset_database()

    def wfs_test_national_labor_calculator(self):

        conn = mongo_client.MongoClient("localhost", 27017)
        mds = conn["itest_mds"]

        mds.labor.insert([
            self.__create_labor_document("New York", "unemployment", 2013, "M01", 10),
            self.__create_labor_document("New York", "unemployment", 2013, "M02", 20),
            self.__create_labor_document("New York", "unemployment", 2013, "M03", 30),
            self.__create_labor_document("New York", "unemployment", 2013, "M04", 40),

            self.__create_labor_document("New York", "labor force", 2013, "M01", 50),
            self.__create_labor_document("New York", "labor force", 2013, "M02", 60),
            self.__create_labor_document("New York", "labor force", 2013, "M03", 70),
            self.__create_labor_document("New York", "labor force", 2013, "M04", 80),

            self.__create_labor_document("New Taco", "unemployment", 2013, "M01", 10),
            self.__create_labor_document("New Taco", "unemployment", 2013, "M02", 20),
            self.__create_labor_document("New Taco", "unemployment", 2013, "M03", 30),
            self.__create_labor_document("New Taco", "unemployment", 2013, "M04", 40),

            self.__create_labor_document("New Taco", "labor force", 2013, "M01", 50),
            self.__create_labor_document("New Taco", "labor force", 2013, "M02", 60),
            self.__create_labor_document("New Taco", "labor force", 2013, "M03", 70),
            self.__create_labor_document("New Taco", "labor force", 2013, "M04", 80)
        ])

        calc = NationalLaborCalculator({"context": self.context})
        calc.run()

        geographies = list(mds.geography.find({
            "name": "United States of America",
            "data.type": "country"
        }))

        self.test_case.assertEqual(len(geographies), 1)

        geo = geographies[0]
        self.test_case.assertDictEqual(geo, {
            "_id": geo["_id"],
            "interval": geo["interval"],
            "meta": geo["meta"],
            "entity_type": "geography",
            "name": "United States of America",
            "data": {
                "type": "country",
                "analytics": {
                    "monthly": {
                        "unemployment_rate": [
                            {
                                "date": "2013-04-01T00:00:00",
                                "value": 50.0
                            },
                            {
                                "date": "2013-03-01T00:00:00",
                                "value": 30.0 / 70.0 * 100.0
                            },
                            {
                                "date": "2013-02-01T00:00:00",
                                "value": 20.0 / 60.0 * 100.0
                            },
                            {
                                "date": "2013-01-01T00:00:00",
                                "value": 20.0
                            }
                        ]
                    }
                }
            }
        })

    def __create_labor_document(self, area_text, measure_text, year, period, value):

        return {
            "area_text": area_text,
            "area_type_code": "A",
            "measure_text": measure_text,
            "year": year,
            "period": period,
            "value": value
        }
