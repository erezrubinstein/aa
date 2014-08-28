from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.data_access_helpers import find_raw_helper
from core.service.svc_master_data_storage.implementation.entity_hierarchy_creator import EntityHierarchyCreator
from core.common.utilities.errors import BadRequestError
from core.common.utilities.helpers import generate_id
import mox
import pprint


__author__ = 'vgold'


class EntityHierarchyCreatorTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(EntityHierarchyCreatorTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on instance for calls to record
        self.mock = self.mox.CreateMock(EntityHierarchyCreator)
        self.mock.db = self.mox.CreateMockAnything()
        self.mock.find_raw_helper = self.mox.CreateMockAnything()
        self.mock.time_interval_helper = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

    def doCleanups(self):

        super(EntityHierarchyCreatorTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # EntityHierarchyCreator._process_params()

    def test_process_params(self):

        ehc = EntityHierarchyCreator.__new__(EntityHierarchyCreator)

        correct_params = {
            "root_query": {},
            "entity_fields": ["_id"],
            "options": {
                "return_format": "list"
            }
        }

        correct_params2 = dict(correct_params, options={})
        correct_params3 = dict(correct_params, options={"return_format": "asdf"})
        correct_params4 = {
            "root_query": {},
            "options": {}
        }
        correct_params5 = {
            "root_query": {},
            "link_filters": ["asdf", "asdf", "asdf", {}],
            "entity_fields": ["_id"]
        }

        correct_inputs = {
            "entity_type": "entity_type",
            "params": correct_params
        }
        correct_inputs2 = dict(correct_inputs, params=correct_params2)
        correct_inputs3 = dict(correct_inputs, params=correct_params3)
        correct_inputs4 = dict(correct_inputs, params=correct_params4)
        correct_inputs5 = dict(correct_inputs, params=correct_params5)

        self.__assign_attr_from_dict(ehc, dict(correct_inputs, entity_type=None))
        self.assertRaises(BadRequestError, ehc._process_params)

        self.__assign_attr_from_dict(ehc, dict(correct_inputs, params=dict(correct_params, root_query=None)))
        self.assertRaises(BadRequestError, ehc._process_params)

        self.__assign_attr_from_dict(ehc, dict(correct_inputs, params=dict(correct_params, link_filters=None)))
        self.assertRaises(BadRequestError, ehc._process_params)

        self.__assign_attr_from_dict(ehc, dict(correct_inputs, params=dict(correct_params, entity_fields=None)))
        self.assertRaises(BadRequestError, ehc._process_params)

        self.__assign_attr_from_dict(ehc, dict(correct_inputs, params=dict(correct_params, options=None)))
        self.assertRaises(BadRequestError, ehc._process_params)

        # Correct
        self.__assign_attr_from_dict(ehc, correct_inputs)
        result = ehc._process_params()
        self.assertEqual(result, ehc)

        self.__assign_attr_from_dict(ehc, correct_inputs2)
        result = ehc._process_params()
        self.assertEqual(result, ehc)

        self.__assign_attr_from_dict(ehc, correct_inputs3)
        result = ehc._process_params()
        self.assertEqual(result, ehc)

        self.__assign_attr_from_dict(ehc, correct_inputs4)
        result = ehc._process_params()
        self.assertEqual(result, ehc)

        self.__assign_attr_from_dict(ehc, correct_inputs5)
        result = ehc._process_params()
        self.assertEqual(result, ehc)

    ##########################################################################
    # EntityHierarchyCreator._build_relationship_maps()

    def test_build_relationship_maps(self):

        fields_with_links = {"_id": 1, "links": 1}
        entity_query = {}
        entity_type = "company"
        sorted_fields = "sorted_fields"
        return_format = "return_format"
        time_context = None

        entity_id = generate_id()
        root_entity_ids = [entity_id]

        child_id1 = generate_id()
        link1 = {
            "entity_id_to": child_id1
        }
        child_id2 = generate_id()
        link2 = {
            "entity_id_to": child_id2
        }

        entity1 = {
            "_id": entity_id,
            "links": {
                "company": {
                    "retailer_branding": [link1, link2]
                }
            }
        }

        child1 = {
            "_id": child_id1,
            "links": {
                "company": {}
            }
        }

        child2 = {
            "_id": child_id2,
            "links": {}
        }

        self.mock._form_time_context_query(time_context).AndReturn({})

        # First while loop iteration
        self.mock.db.find(entity_type, {"_id": {"$in": [entity_id]}}, fields=fields_with_links).AndReturn([entity1])
        self.mock._process_entity_with_fields(entity1, sorted_fields, return_format).AndReturn(entity1)

        self.mock._test_and_add_link(str(entity_id), link1).AndReturn({"type": "company", "id": child_id1, "recursive": True})
        self.mock._test_and_add_link(str(entity_id), link2).AndReturn({"type": "company", "id": child_id2, "recursive": True})

        # Second while loop iteration
        self.mock.db.find(entity_type, mox.IgnoreArg(), fields=fields_with_links).AndReturn([child1, child2])
        self.mock._process_entity_with_fields(child1, sorted_fields, return_format).AndReturn(child1)
        self.mock._process_entity_with_fields(child2, sorted_fields, return_format).AndReturn(child2)

        self.mox.ReplayAll()

        self.mock.entity_query = entity_query
        self.mock.entity_type = entity_type
        self.mock.fields_with_links = fields_with_links
        self.mock.entity_id = entity_id
        self.mock.sorted_fields = sorted_fields
        self.mock.return_format = return_format
        self.mock.time_context = time_context
        self.mock.root_entity_ids = root_entity_ids
        result = EntityHierarchyCreator._build_relationship_maps(self.mock)

        self.assertEqual(result, self.mock)

        self.assertItemsEqual(self.mock.entity_map.keys(), [str(entity_id), str(child_id1), str(child_id2)])

    ##########################################################################
    # EntityHierarchyCreator._test_and_add_link()

    def test_test_and_add_link__regular_filter(self):

        link_filters = "link_filters"

        entity_id = str(generate_id())

        id_to = generate_id()
        role_from = "role_from"
        role_to = "role_to"
        rel_type = "rel_type"
        type_from = "type_from"
        type_to = "type_to"

        link = {
            "interval": None,
            "entity_id_to": id_to,
            "entity_role_from": role_from,
            "entity_role_to": role_to,
            "relation_type": rel_type,
            "entity_type_from": type_from,
            "entity_type_to": type_to
        }

        self.mock._link_filter_is_recursive(link_filters, link).AndReturn(True)
        self.mock._test_link_against_filter(link_filters, link).AndReturn(True)
        self.mock._add_child_and_parent_for_link(str(id_to), entity_id, link["entity_role_from"],
                                                 link["entity_role_to"], link["relation_type"],
                                                 link["entity_type_from"], link["entity_type_to"])

        self.mox.ReplayAll()

        self.mock.link_filters = link_filters
        self.mock.bidirectional_links = True
        result = EntityHierarchyCreator._test_and_add_link(self.mock, entity_id, link)

        self.assertEqual(result["id"], id_to)
        self.assertEqual(result["type"], type_to)
        self.assertEqual(result["recursive"], True)

    def test_test_and_add_link__regular_filter__not_recursive(self):

        link_filters = "link_filters"

        entity_id = str(generate_id())

        id_to = generate_id()
        role_from = "role_from"
        role_to = "role_to"
        rel_type = "rel_type"
        type_from = "type_from"
        type_to = "type_to"

        link = {
            "interval": None,
            "entity_id_to": id_to,
            "entity_role_from": role_from,
            "entity_role_to": role_to,
            "relation_type": rel_type,
            "entity_type_from": type_from,
            "entity_type_to": type_to
        }

        self.mock._link_filter_is_recursive(link_filters, link).AndReturn(False)
        self.mock._test_link_against_filter(link_filters, link).AndReturn(True)
        self.mock._add_child_and_parent_for_link(str(id_to), entity_id, link["entity_role_from"],
                                                 link["entity_role_to"], link["relation_type"],
                                                 link["entity_type_from"], link["entity_type_to"])

        self.mox.ReplayAll()

        self.mock.link_filters = link_filters
        self.mock.bidirectional_links = True
        result = EntityHierarchyCreator._test_and_add_link(self.mock, entity_id, link)

        self.assertEqual(result["id"], id_to)
        self.assertEqual(result["type"], type_to)
        self.assertEqual(result["recursive"], False)

    def test_test_and_add_link__opposite_filter(self):

        link_filters = "link_filters"

        entity_id = str(generate_id())

        id_to = generate_id()
        role_from = "role_from"
        role_to = "role_to"
        rel_type = "rel_type"
        type_from = "type_from"
        type_to = "type_to"

        link = {
            "interval": None,
            "entity_id_to": id_to,
            "entity_role_from": role_from,
            "entity_role_to": role_to,
            "relation_type": rel_type,
            "entity_type_from": type_from,
            "entity_type_to": type_to
        }

        self.mock._link_filter_is_recursive(link_filters, link).AndReturn(True)
        self.mock._test_link_against_filter(link_filters, link).AndReturn(False)
        self.mock._test_link_against_filter(link_filters, link, opposite = True).AndReturn(True)
        self.mock._add_child_and_parent_for_link(entity_id, str(id_to), link["entity_role_to"],
                                                 link["entity_role_from"], link["relation_type"],
                                                 link["entity_type_to"], link["entity_type_from"])

        self.mox.ReplayAll()

        self.mock.link_filters = link_filters
        self.mock.bidirectional_links = True
        result = EntityHierarchyCreator._test_and_add_link(self.mock, entity_id, link)

        self.assertEqual(result["id"], id_to)
        self.assertEqual(result["type"], type_to)
        self.assertEqual(result["recursive"], True)

    ##########################################################################
    # EntityHierarchyCreator._add_child_and_parent_for_link()

    def test_add_child_and_parent_for_link(self):

        ehc = EntityHierarchyCreator.__new__(EntityHierarchyCreator)

        cid = "cid"
        pid = "pid"
        role_from = "role_from"
        role_to = "role_to"
        relation_type = "relation_type"
        type_from = "type_from"
        type_to = "type_to"

        ehc.parent_to_child_map = {}
        ehc.child_to_parent_map = {}
        ehc._add_child_and_parent_for_link(cid, pid, role_from, role_to, relation_type, type_from, type_to)

        self.assertDictEqual(ehc.parent_to_child_map, {pid: {cid: dict(_id = cid,
                                                                       entity_role_from = role_from,
                                                                       entity_role_to = role_to,
                                                                       entity_type_from = type_from,
                                                                       entity_type_to = type_to,
                                                                       relation_type = relation_type)}})
        self.assertDictEqual(ehc.child_to_parent_map, {cid: {pid: dict(_id = pid,
                                                                       entity_role_from = role_to,
                                                                       entity_role_to = role_from,
                                                                       entity_type_from = type_to,
                                                                       entity_type_to = type_from,
                                                                       relation_type = relation_type)}})

    ##########################################################################
    # EntityHierarchyCreator._test_link_against_filter()

    def test_test_link_against_filter__all(self):

        f1 = "_all"
        link = {
            "entity_role_from": "entity_role_from",
            "entity_role_to": "entity_role_to",
            "relation_type": "relation_type"
        }

        hierarchy_creator = EntityHierarchyCreator.__new__(EntityHierarchyCreator)
        hierarchy_creator.time_context = None

        result = hierarchy_creator._test_link_against_filter(f1, link)
        self.assertEqual(result, True)

    def test_test_link_against_filter__dict(self):

        f1 = ["entity_role_from", "entity_role_to", "relation_type"]

        link1 = {
            "entity_role_from": "entity_role_from",
            "entity_role_to": "entity_role_to",
            "relation_type": "relation_type"
        }

        hierarchy_creator = EntityHierarchyCreator.__new__(EntityHierarchyCreator)
        hierarchy_creator.time_context = None

        result = hierarchy_creator._test_link_against_filter(f1, link1)
        self.assertEqual(result, True)

        link2 = {
            "entity_role_from": "entity_role_from",
            "entity_role_to": "entity_role_to",
            "relation_type": "asdf"
        }

        hierarchy_creator = EntityHierarchyCreator.__new__(EntityHierarchyCreator)
        hierarchy_creator.time_context = None

        result = hierarchy_creator._test_link_against_filter(f1, link2)
        self.assertEqual(result, False)

        f2 = ["entity_role_from", "entity_role_to", "_all"]

        link1 = {
            "entity_role_from": "entity_role_from",
            "entity_role_to": "entity_role_to",
            "relation_type": "relation_type"
        }

        hierarchy_creator = EntityHierarchyCreator.__new__(EntityHierarchyCreator)
        hierarchy_creator.time_context = None

        result = hierarchy_creator._test_link_against_filter(f2, link1)
        self.assertEqual(result, True)

        link2 = {
            "entity_role_from": "entity_role_from",
            "entity_role_to": "entity_role_to",
            "relation_type": "asdf"
        }

        hierarchy_creator = EntityHierarchyCreator.__new__(EntityHierarchyCreator)
        hierarchy_creator.time_context = None

        result = hierarchy_creator._test_link_against_filter(f2, link2)
        self.assertEqual(result, True)

    ##########################################################################
    # EntityHierarchyCreator._link_filter_is_recursive()

    def test_link_filter_is_recursive__all(self):

        f1 = "_all"
        link = {
            "entity_role_from": "entity_role_from",
            "entity_role_to": "entity_role_to",
            "relation_type": "relation_type"
        }

        result = EntityHierarchyCreator._link_filter_is_recursive(f1, link)
        self.assertEqual(result, True)

    def test_link_filter_is_recursive__list(self):

        link = {
            "entity_role_from": "entity_role_from",
            "entity_role_to": "entity_role_to",
            "relation_type": "relation_type"
        }

        f1 = ["entity_role_from", "entity_role_to", "relation_type"]

        result = EntityHierarchyCreator._link_filter_is_recursive(f1, link)
        self.assertEqual(result, True)

        f2 = ["entity_role_from", "entity_role_to", "relation_type", {"recursive": True}]

        result = EntityHierarchyCreator._link_filter_is_recursive(f2, link)
        self.assertEqual(result, True)

        f3 = ["entity_role_from", "entity_role_to", "relation_type", {"recursive": False}]

        result = EntityHierarchyCreator._link_filter_is_recursive(f3, link)
        self.assertEqual(result, False)

    def test_link_filter_is_recursive__list_of_lists(self):

        link = {
            "entity_role_from": "entity_role_from",
            "entity_role_to": "entity_role_to",
            "relation_type": "relation_type"
        }

        f1 = [["entity_role_from", "entity_role_to", "relation_type"],
              ["entity_role_to", "entity_role_from", "relation_type"]]

        result = EntityHierarchyCreator._link_filter_is_recursive(f1, link)
        self.assertEqual(result, True)

        f2 = [["entity_role_to", "entity_role_from", "relation_type"],
              ["entity_role_from", "entity_role_to", "relation_type", {"recursive": True}]]

        result = EntityHierarchyCreator._link_filter_is_recursive(f2, link)
        self.assertEqual(result, True)

        f3 = [["entity_role_to", "entity_role_from", "relation_type"],
              ["entity_role_from", "entity_role_to", "relation_type", {"recursive": False}]]

        result = EntityHierarchyCreator._link_filter_is_recursive(f3, link)
        self.assertEqual(result, False)

    ##########################################################################
    # EntityHierarchyCreator._process_entity_with_fields()

    def test_process_entity_with_fields(self):

        return_format = "dict"
        sorted_fields = ["_id", "name", "data.label"]

        entity = {
            "_id": "a",
            "name": "b",
            "data": {
                "label": "c"
            }
        }

        hierarchy_creator = EntityHierarchyCreator.__new__(EntityHierarchyCreator)
        hierarchy_creator.find_raw_helper = find_raw_helper

        result = hierarchy_creator._process_entity_with_fields(entity, sorted_fields, return_format)
        self.assertDictEqual(result, {"_id": "a", "name": "b", "data.label": "c"})

        return_format = "list"
        result = hierarchy_creator._process_entity_with_fields(entity, sorted_fields, return_format)
        self.assertListEqual(result, ["a", "b", "c"])

    #---------------------# Private Helpers #---------------------#

    @staticmethod
    def __assign_attr_from_dict(obj, value_dict):

        for key, value in value_dict.iteritems():
            setattr(obj, key, value)