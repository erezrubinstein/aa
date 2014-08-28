from core.common.business_logic.index_generator import APIIndexParser, NormalIndex, CompoundIndex, GeoSpatialIndex, HashedIndex

__author__ = 'erezrubinstein'

import unittest


class IndexesDataTests(unittest.TestCase):

    def setUp(self):
        # create new mock connection
        self.conn = MockMongoDBCollectionConnection()

    def test_parsing_exception__no_entity_types(self):
        # create index
        indexes = {
            "address":
                [
                    {
                        "index_type" : "normal",
                        "fields": ["data.latitude"]
                    }
                ]
        }

        # parse and ensure that an exception happened
        self.assertRaisesRegexp(Exception, "^Must have entity_types as root element$", APIIndexParser, indexes)


    def test_parsing_exception__fields_must_be_there(self):
        # create index
        indexes = {
            "entity_types":
                {
                    "address":
                        [
                            {
                                "index_type" : "normal",
                            }
                        ]
                }
        }

        # parse and ensure that an exception happened
        self.assertRaisesRegexp(Exception, "^A field name is required$", APIIndexParser, indexes)


    def test_parsing_exception__one_field_required(self):
        # create index
        indexes = {
            "entity_types":
                {
                    "address":
                        [
                            {
                                "index_type" : "normal",
                                "fields": ""
                            }
                        ]
                }
        }

        # parse and ensure that an exception happened
        self.assertRaisesRegexp(Exception, "^A field name is required$", APIIndexParser, indexes)


    def test_parsing_exception__known_index_types_only(self):
        # create index
        indexes = {
            "entity_types":
                {
                    "address":
                        [
                            {
                                "index_type" : "woot",
                                "fields": ["chicken"]
                            }
                        ]
                }
        }

        # parse and ensure that an exception happened
        self.assertRaisesRegexp(Exception, "^Unknown index type \(woot\)$", APIIndexParser, indexes)


    def test_create_normal_index(self):
        # create index
        indexes = {
            "entity_types":
                {
                    "address":
                        [
                            {
                                "index_type" : "normal",
                                "field": "woot",
                                "options":{
                                    "chicken": True
                                }
                            }
                        ]
                }
        }

        # parse indexes
        index_parser = APIIndexParser(indexes)

        # make sure one index was created for one entity
        self.assertEqual(len(index_parser.entities), 1)
        self.assertEqual(len(index_parser.entities["address"]), 1)
        self.assertIsInstance(index_parser.entities["address"][0], NormalIndex)
        self.assertEqual(index_parser.entities["address"][0].index_fields, "woot")
        self.assertEqual(index_parser.entities["address"][0].index_options, { "chicken": True })

        # create index and verify all is correct
        index_parser.entities["address"][0].ensure_index(self.conn)
        self.assertEqual(self.conn.index_field, "woot")
        self.assertFalse(self.conn.unique)
        self.assertEqual(self.conn.kwargs, {'background': True})


    def test_compound_index__directions_required(self):
        indexes = {
            "entity_types":
                {
                    "address":
                        [
                            {
                                "index_type" : "compound",
                                "fields": ["data.latitude", "data.longitude"],
                                "options":
                                    {
                                    }
                            }
                        ]
                }
        }

        # parse and ensure that an exception happened
        self.assertRaisesRegexp(Exception, "^IndexQualifiers are required$", APIIndexParser, indexes)


    def test_compound_index__same_len_directions_as_fields_required(self):
        indexes = {
            "entity_types":
                {
                    "address":
                        [
                            {
                                "index_type" : "compound",
                                "fields": ["data.latitude", "data.longitude"],
                                "options":
                                    {
                                        "index_qualifiers":
                                            {
                                                "data.latitude": 1
                                            }
                                    }
                            }
                        ]
                }
        }

        # parse and ensure that an exception happened
        self.assertRaisesRegexp(Exception, "^Same number of IndexQualifiers as fields must be passed in$", APIIndexParser, indexes)


    def test_compound_index__no_name(self):
        indexes = {
            "entity_types":
                {
                    "address":
                        [
                            {
                                "index_type" : "compound",
                                "fields": ["data.latitude", "data.longitude"],
                                "options":
                                    {
                                        "index_qualifiers":
                                            {
                                                "data.latitude": 1,
                                                "data.longitude": 1
                                            }
                                    }
                            }
                        ]
                }
        }

        # parse indexes
        index_parser = APIIndexParser(indexes)

        # make sure one index was created for one entity
        self.assertEqual(len(index_parser.entities), 1)
        self.assertEqual(len(index_parser.entities["address"]), 1)
        self.assertIsInstance(index_parser.entities["address"][0], CompoundIndex)
        self.assertEqual(index_parser.entities["address"][0].index_fields, ["data.latitude", "data.longitude"])
        self.assertEqual(index_parser.entities["address"][0].index_qualifiers, { "data.latitude": 1, "data.longitude": 1 })

        # create index and verify all is correct
        index_parser.entities["address"][0].ensure_index(self.conn)
        self.assertEqual(self.conn.index_field, [("data.latitude", 1), ("data.longitude",1)])
        self.assertFalse(self.conn.unique)
        self.assertEqual(self.conn.kwargs, {'background': True})


    def test_compound_index__with_name(self):
        indexes = {
            "entity_types":
                {
                    "address":
                        [
                            {
                                "index_type" : "compound",
                                "fields": ["data.latitude", "data.longitude"],
                                "options":
                                    {
                                        "index_qualifiers":
                                            {
                                                "data.latitude": 1,
                                                "data.longitude": 1
                                            },
                                        "name": "wandering-bear"
                                    }
                            }
                        ]
                }
        }

        # parse indexes
        index_parser = APIIndexParser(indexes)

        # make sure one index was created for one entity
        self.assertEqual(len(index_parser.entities), 1)
        self.assertEqual(len(index_parser.entities["address"]), 1)
        self.assertIsInstance(index_parser.entities["address"][0], CompoundIndex)
        self.assertEqual(index_parser.entities["address"][0].index_fields, ["data.latitude", "data.longitude"])
        self.assertEqual(index_parser.entities["address"][0].index_qualifiers, { "data.latitude": 1, "data.longitude": 1 })

        # create index and verify all is correct
        index_parser.entities["address"][0].ensure_index(self.conn)
        self.assertEqual(self.conn.index_field, [("data.latitude", 1), ("data.longitude",1)])
        self.assertFalse(self.conn.unique)
        self.assertEqual(self.conn.kwargs, {"name": "wandering-bear", 'background': True})


    def test_compound_index__with_different_types(self):
        indexes = {
            "entity_types":
                {
                    "address":
                        [
                            {
                                "index_type" : "compound",
                                "fields": ["data.name", "data.geo"],
                                "options":
                                    {
                                        "index_qualifiers":
                                            {
                                                "data.name": 1,
                                                "data.geo": "2dsphere"
                                            }
                                    }
                            }
                        ]
                }
        }

        # parse indexes
        index_parser = APIIndexParser(indexes)

        # make sure one index was created for one entity
        self.assertEqual(len(index_parser.entities), 1)
        self.assertEqual(len(index_parser.entities["address"]), 1)
        self.assertIsInstance(index_parser.entities["address"][0], CompoundIndex)
        self.assertEqual(index_parser.entities["address"][0].index_fields, ["data.name", "data.geo"])
        self.assertEqual(index_parser.entities["address"][0].index_qualifiers, { "data.name": 1, "data.geo": "2dsphere" })

        # create index and verify all is correct
        index_parser.entities["address"][0].ensure_index(self.conn)
        self.assertEqual(self.conn.index_field, [("data.name", 1), ("data.geo","2dsphere")])
        self.assertFalse(self.conn.unique)
        self.assertEqual(self.conn.kwargs, {'background': True})


    def test_geospatial_index(self):
        indexes = {
            "entity_types":
                {
                    "address":
                        [
                            {
                                "index_type" : "geospatial",
                                "fields": ["data.geo"]
                            }
                        ]
                }
        }

        # parse indexes
        index_parser = APIIndexParser(indexes)

        # make sure one index was created for one entity
        self.assertEqual(len(index_parser.entities), 1)
        self.assertEqual(len(index_parser.entities["address"]), 1)
        self.assertIsInstance(index_parser.entities["address"][0], GeoSpatialIndex)
        self.assertEqual(index_parser.entities["address"][0].index_fields, ["data.geo"])

        # create index and verify all is correct
        index_parser.entities["address"][0].ensure_index(self.conn)
        self.assertEqual(self.conn.index_field, [("data.geo", "2dsphere")])
        self.assertFalse(self.conn.unique)
        self.assertEqual(self.conn.kwargs, {'background': True})


    def test_hashed_index(self):
        indexes = {
            "entity_types":
                {
                    "address":
                        [
                            {
                                "index_type" : "hashed",
                                "field": "_id"
                            }
                        ]
                }
        }

        # parse indexes
        index_parser = APIIndexParser(indexes)

        # make sure one index was created for one entity
        self.assertEqual(len(index_parser.entities), 1)
        self.assertEqual(len(index_parser.entities["address"]), 1)
        self.assertIsInstance(index_parser.entities["address"][0], HashedIndex)
        self.assertEqual(index_parser.entities["address"][0].index_fields, "_id")

        # create index and verify all is correct
        index_parser.entities["address"][0].ensure_index(self.conn)
        self.assertEqual(self.conn.index_field, [("_id", "hashed")])
        self.assertFalse(self.conn.unique)
        self.assertEqual(self.conn.kwargs, {'background': True})



    def test_multiple_entities(self):
        indexes = {
            "entity_types":
                {
                    "address":
                        [
                            {
                                "index_type" : "normal",
                                "field": "data.latitude"
                            }
                        ],
                    "store":
                        [
                            {
                                "index_type" : "normal",
                                "field": "links.company.store_ownership.entity_id_to"
                            }
                        ]
                }
        }

        # parse indexes
        index_parser = APIIndexParser(indexes)

        # make sure we have one index for two entities
        self.assertEqual(len(index_parser.entities), 2)
        self.assertEqual(len(index_parser.entities["address"]), 1)
        self.assertEqual(len(index_parser.entities["store"]), 1)
        self.assertIsInstance(index_parser.entities["address"][0], NormalIndex)
        self.assertIsInstance(index_parser.entities["store"][0], NormalIndex)
        self.assertEqual(index_parser.entities["address"][0].index_fields, "data.latitude")
        self.assertEqual(index_parser.entities["store"][0].index_fields, "links.company.store_ownership.entity_id_to")




class MockMongoDBCollectionConnection(object):
    """
    Mock MongoDB collection connection class
    """
    def ensure_index(self, index, unique = False, **kwargs):
        self.index_field = index
        self.unique = unique
        self.kwargs = kwargs


if __name__ == '__main__':
    unittest.main()
