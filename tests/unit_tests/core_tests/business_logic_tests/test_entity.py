from __future__ import division
from core.common.utilities.include import *

import unittest

from common.utilities.inversion_of_control      import dependencies, Dependency
from common.helpers.common_dependency_helper    import register_common_mock_dependencies

from core.common.utilities.errors               import *
from core.common.utilities.helpers              import *
from core.common.business_logic.entity          import BusinessEntity

__author__ = 'vahram'

###################################################################################################

class BusinessEntityTests(unittest.TestCase):

    def setUp(self):

        register_common_mock_dependencies()

        self.maxDiff = None
        self.time_init = get_current_timestamp()
        self.context_data = {
            "source": "test_entity.py",
            "user_id": "42"
        }

        self.time_init_prev1 = self.time_init - datetime.timedelta(days = 1)
        self.time_init_next1 = self.time_init + datetime.timedelta(days = 1)
        self.time_init_prev2 = self.time_init - datetime.timedelta(days = 2)
        self.time_init_next2 = self.time_init + datetime.timedelta(days = 2)

    def tearDown(self):

        dependencies.clear()

    ##------------------------------------ Private Methods --------------------------------------##

    def __entity_standard_init(self, entity_type="company"):

        return BusinessEntity.standard_init(generate_id(),
                                            entity_type,
                                            "Sample Company ID",
                                            time_creation = self.time_init,
                                            interval =
                                               (
                                                   self.time_init_prev1,
                                                   self.time_init_next1
                                               ),
                                            data =
                                               {
                                                   "name": "Sample Company",
                                                   "type": "retail_parent",
                                                   "extra": {"random_field": 123},
                                                   "deep": {"x": {"y": "z"}, "u": "v"}
                                               },
                                            meta =
                                               {
                                                   "extra": {"random_field": "testing init"},
                                                   "created_by": {
                                                       "source": "test_entity.py",
                                                       "user_id": None
                                                   }
                                               }
        )


    def __init_entity_db_rec(self):

        path = "data"
        filename = "test_entity.json"
        with open(os.path.join(path, filename)) as fin:

            entity_rec = json.load(fin)
            result = BusinessEntity.web_rec_init(entity_rec)

        return result

    def __add_links_to_entity(self, entity):

        entity.register_context({"source": "test_add_links", "user_id": "42"})

        entity.add_link(relation_type = "sample_relation",
                        entity_role_from = "role_parent",
                        entity_role_to = "role_child",
                        entity_type_to = "company",
                        entity_id_to = "12345",
                        link_interval =
                        (
                            self.time_init_prev2,
                            self.time_init_next2
                        ),
                        link_data =
                        {
                            "strength": 42
                        }
                    )
        entity.add_link(relation_type = "sample_relation",
                        entity_role_from = "role_competitor",
                        entity_role_to = "role_competitor",
                        entity_type_to = "company",
                        entity_id_to = "54321"
                    )
        entity.add_link(relation_type = "another_relation",
                        entity_role_from = "role_parent",
                        entity_role_to = "role_child",
                        entity_type_to = "company",
                        entity_id_to = "12345"
                    )
        entity.add_link(relation_type = "management",
                        entity_role_from = "role_company",
                        entity_role_to = "role_ceo",
                        entity_type_to = "person",
                        entity_id_to = "bill_gates",
                        link_interval =
                        (
                            self.time_init - datetime.timedelta(days = 1),
                            None
                        )
                    )

    ##---------------------------------- Test Initialization ------------------------------------##

    def test_standard_init_success(self):

        entity = self.__entity_standard_init()

        self.assertIsInstance(entity.entity_id, ObjectId)
        self.assertEqual(entity.entity_type, "company")
        self.assertEqual(entity.name, "Sample Company ID")
        self.assertEqual(entity.data["name"], "Sample Company")
        self.assertEqual(entity.data["type"], "retail_parent")
        self.assertEqual(entity.data["extra"]["random_field"], 123)
        self.assertEqual(entity.meta["extra"]["random_field"], "testing init")
        self.assertEqual(entity.meta["created_at"], self.time_init)
        self.assertEqual(entity.meta["updated_at"], self.time_init)

        self.assertTrue(entity.validate())


    def test_standard_init_no_creation_meta_success(self):
        """
        Test that an entity set with creation_meta:"none" in ref data calls a base BusinessData.basic_init with
        require_meta=False
        """
        entity = self.__entity_standard_init("retailer_transaction")

        self.assertEqual(entity.meta, None)

        self.assertTrue(entity.validate())


    def test_dict_init_success(self):

        # TODO get a valid entity JSON (web format) and replace test_entity.json
        pass

    def test_to_dict(self):

        # Initialize two identical dummy entities with links
        entity = self.__entity_standard_init()
        self.__add_links_to_entity(entity)
        entity_other = self.__entity_standard_init()
        self.__add_links_to_entity(entity_other)

        # Link one to the other to test recursive dict encoding
        entity.links["company"]["sample_relation"][0]["entity"] = entity_other
        entity.links["company"]["another_relation"][0]["entity"] = entity_other

        # Get the complete entity records with all the fields present
        entity_rec_all = entity.to_dict(keep_linked_entities = True,
                                        include_all_links = True,
                                        validate_entity = True,
                                        validate_links = True,
                                        deepcopy_data = True,
                                        postproc_params = None)
        #pprint.pprint(entity_rec_all)

        entity_id_all = entity_rec_all["_id"]
        self.assertTrue(is_id_type(entity_id_all))

        # Make sure the top and nested entity records are identical (first delete dates, etc)
        linked_entity_rec = entity_rec_all["links"]["company"]["sample_relation"][0]["entity"]
        for entity_rec in copy.deepcopy([entity_rec_all, linked_entity_rec]):

            del entity_rec["_id"]
            del entity_rec["meta"]["history"]
            del entity_rec["meta"]["updated_at"]
            del entity_rec["links"]
            self.assertEqual(entity_rec,
            {
                'data': {'deep': {'u': 'v', 'x': {'y': 'z'}},
                          'extra': {'random_field': 123},
                          'name': 'Sample Company',
                          'type': 'retail_parent'},
                 'entity_type': 'company',
                 'interval': (
                                 self.time_init_prev1,
                                 self.time_init_next1
                             ),
                 'meta': {
                     'created_at': self.time_init,
                     'extra': {'random_field': 'testing init'},
                     "created_by": {
                         "source": "test_entity.py",
                         "user_id": None
                        }
                 },
                 'name': 'Sample Company ID'
            })

        # Test dict encoding with entity and link post-processing enabled
        postproc_min = \
        {
            "entity_fields": {"_all": ["_id", "entity_type", "name", "data.deep.u"]},
            "link_fields":
            {
                "sample_relation": ["entity_role_from", "entity_role_to"],
                "management": ["interval"]
            }
        }

        entity_rec_min = entity.to_dict(keep_linked_entities = True,
                                        include_all_links = True,
                                        validate_entity = True,
                                        validate_links = True,
                                        deepcopy_data = True,
                                        postproc_params = postproc_min)
        #pprint.pprint(entity_rec_min)

        entity_id_min = entity_rec_min["_id"]
        self.assertEqual(entity_id_all, entity_id_min)

        del entity_rec_min["_id"]
        del entity_rec_min["links"]["company"]["sample_relation"][0]["entity"]["_id"]

        link_interval = (self.time_init_prev1, None)
        self.assertEqual(entity_rec_min,
        {
         'data.deep.u': 'v',
         'entity_type': 'company',
         'links': {'company': {'sample_relation': [{'entity': {'data.deep.u': 'v',
                                                               'entity_type': 'company',
                                                               'links': {'company': {'sample_relation': [{'entity_role_from': 'role_parent',
                                                                                                          'entity_role_to': 'role_child'},
                                                                                                         {'entity_role_from': 'role_competitor',
                                                                                                          'entity_role_to': 'role_competitor'}]},
                                                                         'person': {'management': [{'interval': link_interval}]}},
                                                               'name': 'Sample Company ID'},
                                                    'entity_role_from': 'role_parent',
                                                    'entity_role_to': 'role_child'},
                                                   {'entity_role_from': 'role_competitor',
                                                    'entity_role_to': 'role_competitor'}]},
                   'person': {'management': [{'interval': link_interval}]}},
         'name': 'Sample Company ID'
        })

    ##----------------------------- Test Main Interface - Entity Fields -------------------------##

    def test_get_entity_field(self):

        entity = self.__entity_standard_init()

        self.assertEqual(entity.get_entity_field("name"), "Sample Company ID")
        self.assertEqual(entity.get_entity_field("interval")[0].day, self.time_init_prev1.day)
        self.assertEqual(entity.get_entity_field("interval")[1].day, self.time_init_next1.day)
        self.assertEqual(entity.get_entity_field("data.name"), "Sample Company")
        self.assertEqual(entity.get_entity_field("data.deep.x.y"), "z")
        self.assertEqual(entity.get_entity_field("data.deep.x"), {"y": "z"})
        self.assertEqual(entity.get_entity_field("meta.extra.random_field"), "testing init")

        self.assertRaises(InputError, lambda s: entity.get_entity_field(s), "xyz")
        self.assertRaises(InputError, lambda s: entity.get_entity_field(s), "interval.123")
        self.assertRaises(RecInputError, lambda s: entity.get_entity_field(s), "data.deep.x.y.z")
        self.assertRaises(RecInputError, lambda s: entity.get_entity_field(s), "data.deep.missing")

    def test_update_entity_field(self):

        entity = self.__entity_standard_init()

        entity.register_context(self.context_data)
        entity.update_entity_field("name", "Another Company ID")
        self.assertEqual(entity.get_entity_field("name"), "Another Company ID")
        entity.update_entity_field("data.name", "Another Company")
        self.assertEqual(entity.get_entity_field("data.name"), "Another Company")
        entity.update_entity_field("data.deep.x.y", 42)
        self.assertEqual(entity.get_entity_field("data.deep.x.y"), 42)
        entity.update_entity_field("meta.new", "abc")
        self.assertEqual(entity.get_entity_field("meta.new"), "abc")

        updates = entity.get_new_updates()
        self.assertEqual(len(updates), 4)

        update_timestamps = map(lambda u: u["timestamp"], updates)
        self.assertEqual(sorted(update_timestamps), update_timestamps)

        self.assertEqual(updates[1]["field"], "data.name")
        self.assertEqual(updates[1]["old_value"], "Sample Company")
        self.assertEqual(updates[1]["new_value"], "Another Company")

        self.assertEqual(updates[-1]["field"], "meta.new")
        self.assertEqual(updates[-1]["old_value"], None)
        self.assertEqual(updates[-1]["new_value"], "abc")

    ##----------------------------- Test Main Interface - Links ---------------------------------##

    def test_add_links(self):

        entity = self.__entity_standard_init()
        self.__add_links_to_entity(entity)

        # pprint.pprint(entity.links)

        self.assertIsInstance(entity.links, dict)
        self.assertEqual(set(entity.links.keys()),
                         {"company", "person"})
        self.assertEqual(set(entity.links["company"].keys()),
                         {"sample_relation", "another_relation"})
        self.assertEqual(set(entity.links["person"].keys()),
                         {"management"})

    def test_get_links(self):

        entity = self.__entity_standard_init()
        self.__add_links_to_entity(entity)

        list_links = entity.get_links()
        self.assertEqual(len(list_links), 4)

        list_links_1 = entity.get_links_to_entity_id("sample_relation",
                                                     "role_parent",
                                                     "role_child",
                                                     "company",
                                                     "12345")
        self.assertEqual(len(list_links_1), 1)
        list_links_2 = entity.get_links_to_entity_id("sample_relation",
                                                     "role_competitor",
                                                     "role_competitor",
                                                     "company",
                                                     "54321")
        self.assertEqual(len(list_links_2), 1)
        list_links_3 = entity.get_links_to_entity_id("another_relation",
                                                     "role_parent",
                                                     "role_child",
                                                     "company",
                                                     "12345")
        self.assertEqual(len(list_links_3), 1)


    def test_add_link_to_entity__no_ref_data_match(self):
        """
        This tests adding links that have no ref data match.  Both their ownership will be defaulted to False.
        """

        # test entity
        entity = {
            "_id": "42",
            "name": "UNITTEST_ENTITY",
            "data": {
                "UNITTEST_BATCH_INSERT_WITH_LINKS": True
            }
        }

        # test link data
        link_data = { "woot": "chicken" }

        # add two links
        BusinessEntity.add_link_to_entity(entity, "store", "42", "UNITTEST_ROLE_FROM", "company", "77", "UNITTEST_ROLE_TO", "UNITTEST_RELATIONSHIP", link_data = link_data)
        BusinessEntity.add_link_to_entity(entity, "store", "42", "UNITTEST_ROLE_FROM", "company", "78", "UNITTEST_ROLE_TO", "UNITTEST_RELATIONSHIP")

        # assert entity has correct link structure
        self.assertEqual(len(entity["links"]), 1)
        self.assertEqual(len(entity["links"]["company"]), 1)
        self.assertEqual(len(entity["links"]["company"]["UNITTEST_RELATIONSHIP"]), 2)
        self.assertEqual(len(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][0]), 10)

        # verify all fields
        self.assertIsInstance(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][0]["_id"], ObjectId)
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][0]["entity_type_from"], "store")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][0]["entity_type_to"], "company")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][0]["entity_id_from"], "42")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][0]["entity_id_to"], "77")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][0]["entity_role_from"], "UNITTEST_ROLE_FROM")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][0]["entity_role_to"], "UNITTEST_ROLE_TO")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][0]["relation_type"], "UNITTEST_RELATIONSHIP")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][0]["interval"], None)
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][0]["data"], { "woot": "chicken", "properties": { "ownership": False }})
        # second link
        self.assertIsInstance(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][1]["_id"], ObjectId)
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][1]["entity_type_from"], "store")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][1]["entity_type_to"], "company")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][1]["entity_id_from"], "42")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][1]["entity_id_to"], "78")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][1]["entity_role_from"], "UNITTEST_ROLE_FROM")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][1]["entity_role_to"], "UNITTEST_ROLE_TO")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][1]["relation_type"], "UNITTEST_RELATIONSHIP")
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][1]["interval"], None)
        self.assertEqual(entity["links"]["company"]["UNITTEST_RELATIONSHIP"][1]["data"], { "properties": { "ownership": False }})


    def test_add_link_to_entity__ref_data_match(self):
        """
        This tests adding links that match the ref data.
        The link that matches, will have the same ownership as specified in the ref data JSON.
        """

        # test entity
        entity = {
            "_id": "42",
            "name": "UNITTEST_COMPANY",
            "data": {
                "Woot": "chicken"
            }
        }

        # add two links
        BusinessEntity.add_link_to_entity(entity, "file", "42", "retail_input_file", "retail_input_record", "77", "retail_input_record", "retail_input")
        BusinessEntity.add_link_to_entity(entity, "company", "77", "retail_segment", "company", "42", "retail_parent", "retailer_branding")

        # assert entity has correct link structure
        self.assertEqual(len(entity["links"]), 2)
        self.assertEqual(len(entity["links"]["company"]), 1)
        self.assertEqual(len(entity["links"]["retail_input_record"]), 1)
        self.assertEqual(len(entity["links"]["company"]["retailer_branding"]), 1)
        self.assertEqual(len(entity["links"]["retail_input_record"]["retail_input"]), 1)

        # verify all fields
        self.assertIsInstance(entity["links"]["company"]["retailer_branding"][0]["_id"], ObjectId)
        self.assertEqual(entity["links"]["company"]["retailer_branding"][0]["entity_type_from"], "company")
        self.assertEqual(entity["links"]["company"]["retailer_branding"][0]["entity_type_to"], "company")
        self.assertEqual(entity["links"]["company"]["retailer_branding"][0]["entity_id_from"], "77")
        self.assertEqual(entity["links"]["company"]["retailer_branding"][0]["entity_id_to"], "42")
        self.assertEqual(entity["links"]["company"]["retailer_branding"][0]["entity_role_from"], "retail_segment")
        self.assertEqual(entity["links"]["company"]["retailer_branding"][0]["entity_role_to"], "retail_parent")
        self.assertEqual(entity["links"]["company"]["retailer_branding"][0]["relation_type"], "retailer_branding")
        self.assertEqual(entity["links"]["company"]["retailer_branding"][0]["interval"], None)
        self.assertEqual(entity["links"]["company"]["retailer_branding"][0]["data"], { "properties": { "ownership": False }})
        # second link
        self.assertIsInstance(entity["links"]["retail_input_record"]["retail_input"][0]["_id"], ObjectId)
        self.assertEqual(entity["links"]["retail_input_record"]["retail_input"][0]["entity_type_from"], "file")
        self.assertEqual(entity["links"]["retail_input_record"]["retail_input"][0]["entity_type_to"], "retail_input_record")
        self.assertEqual(entity["links"]["retail_input_record"]["retail_input"][0]["entity_id_from"], "42")
        self.assertEqual(entity["links"]["retail_input_record"]["retail_input"][0]["entity_id_to"], "77")
        self.assertEqual(entity["links"]["retail_input_record"]["retail_input"][0]["entity_role_from"], "retail_input_file")
        self.assertEqual(entity["links"]["retail_input_record"]["retail_input"][0]["entity_role_to"], "retail_input_record")
        self.assertEqual(entity["links"]["retail_input_record"]["retail_input"][0]["relation_type"], "retail_input")
        self.assertEqual(entity["links"]["retail_input_record"]["retail_input"][0]["interval"], None)
        # Key!! ownership is True, not false
        self.assertEqual(entity["links"]["retail_input_record"]["retail_input"][0]["data"], { "properties": { "ownership": True }})






    ##-------------------------------------------------------------------------------------------##

if __name__ == '__main__':
    unittest.main()
