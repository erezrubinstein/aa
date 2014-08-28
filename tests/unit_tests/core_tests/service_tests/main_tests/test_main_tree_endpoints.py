import json
from operator import isCallable
import uuid
import mox
from mox import Func
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.service.svc_main.implementation.service_endpoints.tree_endpoints import TreeEndpoints

__author__ = 'erezrubinstein'

import unittest


class TestMainTreeEndpoints(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(TestMainTreeEndpoints, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock_main_params_builder = Dependency("CoreAPIParamsBuilder").value

        # create mock app
        self.mock_app = self.mox.CreateMockAnything()

        # mock uuid generator
        self.mock_id_generator = self.mox.CreateMockAnything()
        self.mock_id_generator.hex = "woot"
        self.mox.StubOutWithMock(uuid, "uuid4")


    def doCleanups(self):
        # call parent clean up
        super(TestMainTreeEndpoints, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_get_preset_industry_tree_data__preset_cache_called_correctly(self):
        # class that we are testing
        tree_endpoint = TreeEndpoints(None, None)

        # create expected parameters
        cache_rec = tree_endpoint._make_cache_rec(["industry"], "/tree/preset/industries", 'tree')

        # begin recording
        self.mock_app.get_preset_data_with_cache(cache_rec, Func(isCallable), params={},
                                                 data_method_args=()).AndReturn({ "tree": "woot" })

        # replay expectations
        self.mox.ReplayAll()

        # create mock request
        mock_request = self.mox.CreateMockAnything()
        mock_request.args = { "params": "{}" }
        response = tree_endpoint.get_preset_industry_tree_data(self.mock_app, mock_request, "/tree/preset/industries")

        # make sure we get the right response
        self.assertEqual(response, "woot")


    def test_get_preset_industry_tree_data__get_data_method(self):
        # class that we are testing
        tree_endpoint = TreeEndpoints(None, None)

        # stub method to call the get_data method
        def call_get_data(cache_rec, func, params, data_method_args):
            return func(*data_method_args)

        cache_rec = tree_endpoint._make_cache_rec(["industry"], "/tree/preset/industries", 'tree')
        industries_query_params = self.__expected_raw_industries_query_params()

        # create mock industries to return
        mock_industries = self.__fake_raw_industries()

        # begin recording
        self.mock_app.get_preset_data_with_cache(cache_rec, Func(isCallable), params={},
                                                 data_method_args=()).WithSideEffects(call_get_data)
        self.mock_main_access.mds.call_find_entities("industry", params=industries_query_params).AndReturn(mock_industries)
        uuid.uuid4().AndReturn(self.mock_id_generator)

        # replay expectations
        self.mox.ReplayAll()

        # create mock request
        mock_request = self.mox.CreateMockAnything()
        mock_request.args = { "params": "{}" }
        response = tree_endpoint.get_preset_industry_tree_data(self.mock_app, mock_request, "/tree/preset/industries")

        # make sure we get the right response
        self.assertDictEqual(response, self.__expected_parsed_industries())




    # ------------------------------------ Private Methods ------------------------------------

    def __expected_raw_industries_query_params(self):
        return {
            'link_filters': [
                {
                    'filter': {
                        'entity_type_from': 'industry',
                        'entity_type_to': 'industry',
                        'relation_type': 'industry_hierarchy',
                        'entity_role_to': 'child',
                        'entity_role_from': 'parent'
                    },
                    'options': { 'fetch': True, 'recursive': True }
                }
            ],
            'entity_filters': {
                'industry': {
                    '$and': [
                        {
                            'data.industry_level': 1
                        }
                    ]
                }
            },
            'postprocess': {
                'entity_fields': { 'industry': ['_id', 'data'] },
                'link_fields': {'industry_hierarchy': ['entity_role_from', 'entity_role_to', 'entity']}}
        }


    def __fake_raw_industries(self):
        return [
            {
                "_id":"5176d79ef3d31b7fd81ffdd7",
                "data": {
                    "industry_level": 1,
                    "source_vendor": "NAICS",
                    "industry_code": "454312",
                    "source_version": "2007",
                    "source_id": 12.0,
                    "industry_name": "chicken"
                },
                "links": {
                    "industry": {
                        "industry_hierarchy":[
                            {
                                "entity_role_from":"parent",
                                "entity_role_to":"child",
                                "entity": {
                                    "_id":"5176d79df3d31b7fd81ffc8c",
                                    "data": {
                                        "industry_level":2,
                                        "source_vendor":"NAICS",
                                        "industry_code":"441120",
                                        "source_version":"2007",
                                        "source_id":13.0,
                                        "industry_name":"danger zone"
                                    },
                                    "links":{}
                                }
                            }
                        ]
                    }
                }
            }
        ]

    def __expected_parsed_industries(self):
        return {
            '': 'All',
            '_entity_link_level': 0,
            'industry_code': '',
            'children': [
                {
                    '_entity_link_level': 2,
                    'name': 'chicken',
                    'industry_code': '454312',
                    'children': [
                        {
                            '_entity_link_level': 4,
                            'name': 'danger zone',
                            'industry_code': '441120',
                            'children': [],
                            'id': '5176d79df3d31b7fd81ffc8c',
                            'allow_selection': True,
                            'source_id': '441120',
                            'label': '441120 - danger zone',
                            'industry_name': 'danger zone',
                            "publish_competition_for_banners": False
                        }
                    ],
                    'id': '5176d79ef3d31b7fd81ffdd7',
                    'allow_selection': True,
                    'source_id': '454312',
                    'label': '454312 - chicken',
                    'industry_name': 'chicken',
                    "publish_competition_for_banners": False
                }
            ],
            'industry_name': '',
            'allow_selection': False,
            'source_id': '',
            'label': 'All',
            'id': 'woot',
            "publish_competition_for_banners": False
        }



if __name__ == '__main__':
    unittest.main()




