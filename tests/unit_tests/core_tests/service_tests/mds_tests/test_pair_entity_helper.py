from bson.objectid import ObjectId
from core.service.svc_master_data_storage.implementation.pair_entity_helper import get_pair_entity_data_fields, \
    get_entity_data_for_fields, get_linked_entities, get_linked_entity_data
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies
import mox


__author__ = 'vgold'


class PairEntityHelperTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(PairEntityHelperTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on instance for calls to record
        self.mock_db = self.mox.CreateMockAnything()

        self.context = {
            "user_id": "tester",
            "source": "test_pair_entity_creator.py"
        }

    def doCleanups(self):

        super(PairEntityHelperTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # get_pair_entity_data_fields()

    def test_get_entity_sync_fields(self):

        pair_entity_type = "pair_entity_type"

        linked_entities_map = [
            {
                "blah": "blah"
            }
        ]

        entity_type_map = {
            pair_entity_type: {
                "data_fields": [
                    {"field": "type", "sync_on_create": True}
                ],
                "linked_entities": linked_entities_map
            }
        }

        result = get_pair_entity_data_fields(pair_entity_type, entity_type_map)

        entity_fields = {
            "name",
            "interval",
            "data.type"
        }

        self.assertEqual(result, entity_fields)

    ##########################################################################
    # get_entity_data_for_fields()

    def test_get_entity_data_for_fields(self):

        entity_rec = {
            "name": "name",
            "data": {
                "from": {
                    "type": "type",
                    "status": "status"
                },
                "to": {
                    "type": "type",
                    "status": "status"
                },
                "analytics": {
                    "competition": {
                        "monthly": {
                            "store_count": 2
                        }
                    }
                }
            }
        }

        fields = [
            "name",
            "data.from.status",
            "data.analytics.competition.monthly.store_count"
        ]

        expected_result = {
            "name": "name",
            "data": {
                "from": {
                    "status": "status"
                },
                "analytics": {
                    "competition": {
                        "monthly": {
                            "store_count": 2
                        }
                    }
                }
            }
        }

        result = get_entity_data_for_fields(entity_rec, fields)

        self.assertEqual(result, expected_result)

    ##########################################################################
    # get_linked_entities()

    def test_get_linked_entities(self):

        linked_entities_map = [
            {
                "entity_type": "company",
                "relation_type": "retailer_branding",
                "entity_role_from": "retail_segment",
                "entity_role_to": "retail_parent",
                "fields": [
                    "_id",
                    "name"
                ]
            }
        ]

        pair_entity_type = "pair_entity_type"

        ref_data = self.mox.CreateMockAnything()

        ref_data.entity_type_map = {
            pair_entity_type: {
                "entity_type_from": "entity_type_from",
                "entity_type_to": "entity_type_to",
                "data_fields": [
                    "type"
                ],
                "linked_entities": linked_entities_map
            }
        }

        eid1 = ObjectId()
        eid2 = ObjectId()

        entity_dict = {
            "company": {
                eid1: {
                    "links": {
                        "company": {
                            "retailer_branding": [
                                {
                                    "entity_role_from": "retail_segment",
                                    "entity_role_to": "retail_parent",
                                    "entity_id_to": eid2
                                }
                            ]
                        }
                    }
                }
            }
        }

        query = {
            "_id": {"$in": [eid2]}
        }
        projection = {
            "_id": 1,
            "name": 1
        }

        entities = [
            {
                "_id": eid2,
                "name": "HELO"
            }
        ]
        self.mock_db.find("company", query, projection).AndReturn(entities)

        self.mox.ReplayAll()

        results = get_linked_entities(ref_data, pair_entity_type, entity_dict, self.mock_db)

        expected_results = {
            "company": {
                "retailer_branding": {
                    "retail_segment": {
                        "retail_parent": {
                            eid2: {
                                "_id": eid2,
                                "name": "HELO"
                            }
                        }
                    }
                }
            }
        }

        self.assertEqual(results, expected_results)

    ##########################################################################
    # get_linked_entity_data()

    def test_get_linked_entity_data(self):

        eid = ObjectId()

        entity_link = {
            "entity_role_from": "retail_segment",
            "entity_role_to": "retail_parent",
            "entity_id_to": eid
        }

        entity_rec = {
            "links": {
                "company": {
                    "retailer_branding": [entity_link]
                }
            }
        }

        linked_entity = {
            "_id": eid,
            "name": "HELO"
        }

        linked_entities = {
            "company": {
                "retailer_branding": {
                    "retail_segment": {
                        "retail_parent": {
                            eid: linked_entity
                        }
                    }
                }
            }
        }

        expected_result = {
            "company": {
                "retailer_branding": [dict(entity_link, entity=linked_entity)]
            }
        }

        result = get_linked_entity_data(linked_entities, entity_rec)

        self.assertEqual(result, expected_result)



