from __future__ import division
from core.common.utilities.include import *

import unittest

from common.utilities.inversion_of_control      import dependencies, Dependency
from common.helpers.common_dependency_helper    import register_common_mock_dependencies

from core.common.utilities.errors               import *
from core.common.utilities.helpers              import *
from core.common.business_logic.reference_data  import BusinessReferenceData

__author__ = 'vahram'

###################################################################################################

class BusinessEntityTests(unittest.TestCase):

    def setUp(self):

        register_common_mock_dependencies()

    def tearDown(self):

        dependencies.clear()

    ##------------------------------------ Private Methods --------------------------------------##

    def __refdata_standard_init(self):

        self.time_init_refdata = get_current_timestamp()

        self.entity_type_map = \
        {
            "e1":
            {
                "requirements":
                {
                    "data.s": "string",
                    "data.i": "integer",
                    "data.f": "float",
                    "data.n": "number",
                    "data.b": "boolean",
                    "data.x": [1, 2, 3, "xyz"],
                }
            },
            "e2": {}
        }

        self.relation_type_map =\
        {
            "rel1":
            [
                {
                    "from":
                        {
                            "entity_type": "e1",
                            "entity_role": "role1",
                            "requirements": {"data.x": [1, 2, 3]}
                        },
                    "to":
                        {
                            "entity_type": "e2",
                            "entity_role": "role2",
                            "requirements": {"data.x": ["xyz"]}
                        },
                    "properties":
                        {
                            "ownership": False
                        }
                },
                {
                    "from":
                        {
                            "entity_type": "e1",
                            "entity_role": "role1_other",
                            "requirements": {"data.z": "boolean"}
                        },
                    "to":
                        {
                            "entity_type": "e2",
                            "entity_role": "role2_other",
                            "requirements": {"data.z": "string"}
                        },
                    "properties":
                        {
                            "ownership": False
                        }
                }
            ]
        }

        return BusinessReferenceData.standard_init(
                                        self.entity_type_map,
                                        self.relation_type_map,
                                        time_creation = self.time_init_refdata
                                        )

    def __refdata_dict_init(self):

        path = os.path.join(os.path.dirname(__file__), "data")
        filename = "test_reference_data.json"
        with open(os.path.join(path, filename)) as fin:

            ref_data_rec = json.load(fin)
            result = BusinessReferenceData.dict_init(ref_data_rec)

        return result

    ##---------------------------------- Test Initialization ------------------------------------##

    def test_standard_init_success(self):

        refdata = self.__refdata_standard_init()

        self.assertIsInstance(refdata, BusinessReferenceData)
        self.assertIsInstance(refdata.meta, dict)

        self.assertEqual(refdata.meta["updated_at"], self.time_init_refdata)
        self.assertEqual(refdata.meta["created_at"], self.time_init_refdata)

        self.assertIsInstance(refdata.entity_type_map, dict)
        self.assertIsInstance(refdata.relation_type_map, dict)

        self.assertEqual(len(refdata.entity_type_map), 2)
        self.assertEqual(len(refdata.relation_type_map), 1)

        self.assertTrue(refdata.validate())

    def test_dict_init_success(self):

        refdata = self.__refdata_dict_init()

        self.assertIsInstance(refdata, BusinessReferenceData)
        self.assertIsInstance(refdata.meta, dict)

        self.assertLessEqual(refdata.meta["created_at"], refdata.meta["updated_at"])

        self.assertIsInstance(refdata.entity_type_map, dict)
        self.assertIsInstance(refdata.relation_type_map, dict)

        self.assertEqual(len(refdata.entity_type_map), 12)
        self.assertEqual(len(refdata.relation_type_map), 17)

        self.assertTrue(refdata.validate())

    ##---------------------------------- Test Entity Types - Getters ----------------------------##

    def test_entity_type_getters(self):

        refdata = self.__refdata_standard_init()

        self.assertTrue(refdata.is_valid_entity_type("e1"))
        self.assertTrue(refdata.is_valid_entity_type("e2"))
        self.assertFalse(refdata.is_valid_entity_type("e3"))

        self.assertEqual(set(refdata.get_all_entity_types()), {"e1", "e2"})
        self.assertNotEqual(refdata.get_entity_type_info("e1"), {})
        self.assertEqual(refdata.get_entity_type_info("e2"), {})

        validators = refdata.get_entity_type_validators("e1")
        self.assertEqual(set(validators.keys()),
                         {"data.s", "data.i", "data.f", "data.n", "data.b", "data.x"})
        self.assertTrue( validators["data.s"]("x"))
        self.assertFalse(validators["data.s"](1))
        self.assertTrue( validators["data.i"](1))
        self.assertFalse(validators["data.i"]("x"))
        self.assertTrue( validators["data.f"](1.0))
        self.assertFalse(validators["data.f"](1))
        self.assertTrue( validators["data.n"](1.0))
        self.assertTrue( validators["data.n"](1))
        self.assertFalse(validators["data.n"]("x"))
        self.assertTrue( validators["data.b"](False))
        self.assertFalse(validators["data.b"](1))
        self.assertTrue( validators["data.x"](1))
        self.assertTrue( validators["data.x"](2))
        self.assertTrue( validators["data.x"](3))
        self.assertTrue( validators["data.x"]("xyz"))
        self.assertFalse(validators["data.x"]("xy"))

    ##---------------------------------- Test Entity Types - Setters ----------------------------##

    def test_entity_type_setters(self):

        refdata = self.__refdata_standard_init()

        context_data = {
            "source": "test_reference_data.py",
            "user_id": None
        }
        refdata.register_context(context_data)

        self.assertRaises(InputError, lambda s: refdata.add_entity_type(s), "e2")
        self.assertFalse(refdata.is_valid_entity_type("e3"))
        refdata.add_entity_type("e3")
        self.assertTrue(refdata.is_valid_entity_type("e3"))
        refdata.del_entity_type("e3")
        self.assertRaises(InputError, lambda s: refdata.del_entity_type(s), "e3")

        self.assertNotIn("data.y", refdata.get_entity_type_validators("e1"))
        refdata.add_entity_type_required_field("e1", "data.y", field_values = ["Y"])
        self.assertIn("data.y", refdata.get_entity_type_validators("e1"))
        self.assertTrue(refdata.get_entity_type_validators("e1")["data.y"]("Y"))
        self.assertFalse(refdata.get_entity_type_validators("e1")["data.y"]("X"))
        refdata.del_entity_type_required_field("e1", "data.y")
        self.assertNotIn("data.y", refdata.get_entity_type_validators("e1"))

        #pprint.pprint(refdata.meta)

    ##---------------------------------- Test Relation Types - Getters ----------------------------##

    def test_relation_type_getters(self):

        refdata = self.__refdata_standard_init()

        self.assertTrue(refdata.is_valid_relation_type("rel1"))
        self.assertFalse(refdata.is_valid_relation_type("rel2"))

        self.assertEqual(refdata.get_all_relation_types(), ["rel1"])
        self.assertEqual(refdata.get_all_relation_types_for("e1", "e2"), ["rel1"])
        self.assertEqual(refdata.get_all_relation_types_for("e2", "e1"), ["rel1"])
        self.assertEqual(refdata.get_all_relation_types_for("e1", "e1"), [])
        self.assertEqual(len(refdata.get_relation_type_info("rel1")), 2)

        recs_all = refdata.get_relation_records("e1", "e2")
        def f_remove_relation_type(rec):
            self.assertIn("relation_type", rec)
            self.assertEqual(rec["relation_type"], "rel1")
            del rec["relation_type"]
        map(f_remove_relation_type, recs_all)

        self.assertEqual(len(recs_all), 2)
        self.assertEqual(recs_all, self.relation_type_map["rel1"])

        self.assertEqual(len(refdata.get_relation_records("e1", "e3")), 0)
        self.assertEqual(len(refdata.get_relation_records("e1", "e2", relation_types = ["x"])), 0)
        self.assertEqual(len(refdata.get_relation_records("e1", "e2", entity_role_from = "x")), 0)
        self.assertEqual(len(refdata.get_relation_records("e1", "e2", entity_role_to = "x")), 0)

        recs_1 = refdata.get_relation_records("e1", "e2", entity_role_from = "role1")
        map(f_remove_relation_type, recs_1)

        self.assertEqual(len(recs_1), 1)
        self.assertEqual(recs_1[0], self.relation_type_map["rel1"][0])

        recs_2 = refdata.get_relation_records("e1", "e2", entity_role_to = "role2_other")
        map(f_remove_relation_type, recs_2)

        self.assertEqual(len(recs_2), 1)
        self.assertEqual(recs_2[0], self.relation_type_map["rel1"][1])

    def test_real_refdata_relation_type_getters(self):

        refdata = self.__refdata_dict_init()

        recs = refdata.get_relation_records("file", "retail_input_record")
        #print "\n\n".join(pprint.pformat(rec) for rec in recs)

        recs = refdata.get_relation_records("retail_input_record", "file")
        #print "\n\n".join(pprint.pformat(rec) for rec in recs)


    def test_relation_records_validation(self):

        refdata = self.__refdata_dict_init()

        data1 =\
        {
            "type": "retail_parent",
            "test1": "random stuff"
        }
        data2 =\
        {
            "type": "retail_banner",
            "test2": "random stuff"
        }
        data3 =\
        {
            "type": "retail_concept",
            }
        data4 =\
        {
            "name": "Banana Republic",
            }

        rel_recs = refdata.get_relation_records("company",
            "company",
            "retailer_branding",
            "retail_parent",
            "retail_segment")
        self.assertEqual(len(rel_recs), 2)

        validators = refdata.get_relation_record_validators(rel_recs[0])
        self.assertEqual(set(validators.keys()), {"from", "to"})

        self.assertTrue(refdata.validate_relation_data(data1, data2, validators))
        self.assertFalse(refdata.validate_relation_data(data2, data1, validators))
        self.assertFalse(refdata.validate_relation_data(data1, data3, validators))
        self.assertFalse(refdata.validate_relation_data(data1, data4, validators))
        self.assertFalse(refdata.validate_relation_data(data2, data3, validators))
        self.assertFalse(refdata.validate_relation_data(data2, data4, validators))
        self.assertFalse(refdata.validate_relation_data(data3, data4, validators))

        validators = refdata.get_relation_record_validators(rel_recs[1])
        self.assertEqual(set(validators.keys()), {"from", "to"})

        self.assertTrue(refdata.validate_relation_data(data2, data3, validators))
        self.assertFalse(refdata.validate_relation_data(data3, data2, validators))
        self.assertFalse(refdata.validate_relation_data(data1, data2, validators))
        self.assertFalse(refdata.validate_relation_data(data1, data3, validators))
        self.assertFalse(refdata.validate_relation_data(data1, data4, validators))
        self.assertFalse(refdata.validate_relation_data(data2, data4, validators))
        self.assertFalse(refdata.validate_relation_data(data3, data4, validators))

        rel_recs = refdata.get_relation_records("company",
            "company",
            "retailer_branding",
            "retail_segment",
            "retail_parent")
        self.assertEqual(len(rel_recs), 2)

        validators = refdata.get_relation_record_validators(rel_recs[0])
        self.assertEqual(set(validators.keys()), {"from", "to"})

        self.assertTrue(refdata.validate_relation_data(data2, data1, validators))
        self.assertFalse(refdata.validate_relation_data(data1, data2, validators))
        self.assertFalse(refdata.validate_relation_data(data1, data3, validators))
        self.assertFalse(refdata.validate_relation_data(data1, data4, validators))
        self.assertFalse(refdata.validate_relation_data(data2, data3, validators))
        self.assertFalse(refdata.validate_relation_data(data2, data4, validators))
        self.assertFalse(refdata.validate_relation_data(data3, data4, validators))

        validators = refdata.get_relation_record_validators(rel_recs[1])
        self.assertEqual(set(validators.keys()), {"from", "to"})

        self.assertTrue(refdata.validate_relation_data(data3, data2, validators))
        self.assertFalse(refdata.validate_relation_data(data2, data3, validators))
        self.assertFalse(refdata.validate_relation_data(data1, data2, validators))
        self.assertFalse(refdata.validate_relation_data(data1, data3, validators))
        self.assertFalse(refdata.validate_relation_data(data1, data4, validators))
        self.assertFalse(refdata.validate_relation_data(data2, data4, validators))
        self.assertFalse(refdata.validate_relation_data(data3, data4, validators))

    ##---------------------------------- Test Relation Types - Setters ----------------------------##

    def test_relation_type_setters(self):

        refdata = self.__refdata_standard_init()
        context_data = {
            "source": "test_reference_data.py",
            "user_id": None
        }
        refdata.register_context(context_data)

        self.assertRaises(InputError, lambda s: refdata.add_relation_type(s), "rel1")
        self.assertFalse(refdata.is_valid_relation_type("rel2"))
        refdata.add_relation_type("rel2")
        self.assertTrue(refdata.is_valid_relation_type("rel2"))
        self.assertEqual(refdata.get_relation_records("e1", "e2", relation_types = ["rel2"]), [])
        refdata.del_relation_type("rel2")
        self.assertRaises(InputError, lambda s: refdata.del_relation_type(s), "rel2")

        refdata.add_relation_type("rel2")
        refdata.add_relation_record("rel2", "e1", "role A", {}, "e2", "role B", {})
        self.assertEqual(len(refdata.get_relation_records("e1", "e2")), 3)
        refdata.add_relation_record("rel2", "e2", "role C", {}, "e3", "role D", {"data.t":"T"})
        self.assertEqual(len(refdata.get_relation_records("e2", "e3")), 1)
        refdata.del_relation_record("rel2", "e2", "role C", {}, "e3", "role D", {"data.t":"T"})
        self.assertEqual(len(refdata.get_relation_records("e2", "e3")), 0)

    ##-------------------------------------------------------------------------------------------##

if __name__ == '__main__':
    unittest.main()
