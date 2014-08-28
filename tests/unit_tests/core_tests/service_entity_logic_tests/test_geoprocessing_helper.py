import mox
from core.common.business_logic.service_entity_logic import geoprocessing_helper

__author__ = 'spacecowboy et al.'

class WorkflowGeoProcessTests(mox.MoxTestBase):

    def setUp(self):

        super(WorkflowGeoProcessTests, self).setUp()


    def doCleanups(self):

        super(WorkflowGeoProcessTests, self).doCleanups()

    def test_construct_latest_attempt_update_field_value__has_current_method_in_latest_attempt(self):

        geoprocessing_method = 'do_the_hustle_again'
        latest_attempt = {'start_timestamp': 'some_time'}

        entity_rec = {
            'data': {
                'geoprocessing': {
                    'latest_attempt': {
                        'do_the_hustle_again': {
                            'did_the_hustle': 'failed'
                        }
                    }
                }
            }
        }

        field_name, field_value = geoprocessing_helper.construct_latest_attempt_update_field_value(entity_rec, latest_attempt, geoprocessing_method)

        self.assertEqual(field_name, 'data.geoprocessing.latest_attempt.do_the_hustle_again')
        self.assertEqual(field_value, {
            'did_the_hustle': 'failed',
            'start_timestamp': 'some_time'
        })

    def test_construct_latest_attempt_update_field_value__has_different_method_in_latest_attempt(self):

        geoprocessing_method = 'do_the_hustle_again'
        latest_attempt = {'shalalala': 'trolololol'}

        entity_rec = {
            'data': {
                'geoprocessing': {
                    'latest_attempt': {
                        'do_the_hustle': {
                            'did_the_hustle': 'failed'
                        }
                    }
                }
            }
        }

        field_name, field_value = geoprocessing_helper.construct_latest_attempt_update_field_value(entity_rec, latest_attempt, geoprocessing_method)

        self.assertEqual(field_name, 'data.geoprocessing.latest_attempt.do_the_hustle_again')
        self.assertEqual(field_value, {
            'shalalala': 'trolololol'
        })


    def test_construct_latest_attempt_update_field_value__has_latest_attempt(self):

        geoprocessing_method = 'do_the_hustle_again'
        latest_attempt = {'start_timestamp': 'some_time'}

        entity_rec = {
            'data': {
                'geoprocessing': {
                    'latest_attempt': {
                        'did_the_hustle': 'failed'
                    }
                }
            }
        }

        field_name, field_value = geoprocessing_helper.construct_latest_attempt_update_field_value(entity_rec, latest_attempt, geoprocessing_method)

        self.assertEqual(field_name, 'data.geoprocessing.latest_attempt.do_the_hustle_again')
        self.assertEqual(field_value, {
            'start_timestamp': 'some_time'
        })

    def test_construct_latest_attempt_update_field_value__missing_latest_attempt(self):

        geoprocessing_method = 'do_the_hustle_again'
        latest_attempt = {'start_timestamp': 'some_time'}

        entity_rec = {
            'data': {
                'geoprocessing': {
                    'data': {
                        'what': 'is this'
                    }
                }
            }
        }

        field_name, field_value = geoprocessing_helper.construct_latest_attempt_update_field_value(entity_rec, latest_attempt, geoprocessing_method)

        self.assertEqual(field_name, 'data.geoprocessing.latest_attempt')
        self.assertEqual(field_value, {
            'do_the_hustle_again': {
                'start_timestamp': 'some_time'
            }
        })

    def test_construct_latest_attempt_update_field_value__missing_geoprocessing(self):

        geoprocessing_method = 'do_the_hustle_again'
        latest_attempt = {'start_timestamp': 'some_time'}

        entity_rec = {
            'data': {
                'random': 'data'
            }
        }

        field_name, field_value = geoprocessing_helper.construct_latest_attempt_update_field_value(entity_rec, latest_attempt, geoprocessing_method)

        self.assertEqual(field_name, 'data.geoprocessing')
        self.assertEqual(field_value, {
            'latest_attempt': {
                'do_the_hustle_again': {
                    'start_timestamp': 'some_time'
                }
            }
        })