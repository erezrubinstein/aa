from __future__ import division
from core.common.utilities.include import *

import unittest

from common.utilities.inversion_of_control      import dependencies, Dependency
from common.helpers.common_dependency_helper    import register_common_mock_dependencies

from core.common.utilities.errors               import *
from core.common.utilities.helpers              import *
from core.common.business_logic.data            import BusinessData

__author__ = 'vahram'

###################################################################################################

class BusinessEntityTests(unittest.TestCase):

    def setUp(self):

        register_common_mock_dependencies()

    def tearDown(self):

        dependencies.clear()

    ##------------------------------------ Private Methods --------------------------------------##

    def __data_basic_init(self):

        self.time_init_data = get_current_timestamp()
        return BusinessData.basic_init(
            time_creation = self.time_init_data,
            meta =
            {
                "extra": {"random_field": "testing initialization"}
            }
        )

    ##---------------------------------- Test Initialization ------------------------------------##

    def test_basic_init_success(self):

        data = self.__data_basic_init()

        self.assertIsInstance(data, BusinessData)
        self.assertIsInstance(data.meta, dict)

        self.assertIn("created_at", data.meta)
        self.assertIn("updated_at", data.meta)
        self.assertIsInstance(data.meta["created_at"], datetime.datetime)
        self.assertIsInstance(data.meta["updated_at"], datetime.datetime)
        self.assertLessEqual(data.meta["created_at"], data.meta["updated_at"])

        self.assertIn("history", data.meta)
        self.assertIn("updates", data.meta["history"])
        self.assertEqual(data.meta["history"]["updates"], [])

        self.assertIn("extra", data.meta)
        self.assertIn("random_field", data.meta["extra"])
        self.assertEqual(data.meta["extra"]["random_field"], "testing initialization")

        self.assertIsInstance(data.init_timestamp, datetime.datetime)
        self.assertLessEqual(data.meta["updated_at"], data.init_timestamp)

        self.assertIsNone(data.sync_timestamp)

        self.assertTrue(data.validate())

    ##---------------------------------- Test Updating ------------------------------------------##

    def test_updates(self):

        data = self.__data_basic_init()

        updates = data.get_new_updates()
        self.assertEqual(updates, [])
        self.assertLess(data.init_timestamp, data.sync_timestamp)
        first_update_context_data = {
            "source": "test_updates function",
            "user_id": "42"
        }
        second_update_context_data = {
            "source": "test_updates function again",
            "user_id": "42"
        }
        data.register_context(first_update_context_data)
        data.register_update("new_field.1", 123, 456)
        data.register_context(second_update_context_data)
        data.register_update("new_field.2", None, "xyz")
        updates = data.get_new_updates()

        self.assertEqual(len(updates), 2)
        self.assertEqual(updates[0]["field"], "new_field.1")
        self.assertEqual(updates[0]["old_value"], 123)
        self.assertEqual(updates[0]["new_value"], 456)
        self.assertEqual(updates[0]["action"], None)
        self.assertEqual(updates[0]["context"]["source"], "test_updates function")
        self.assertEqual(updates[1]["field"], "new_field.2")
        self.assertEqual(updates[1]["old_value"], None)
        self.assertEqual(updates[1]["new_value"], "xyz")
        self.assertEqual(updates[1]["action"], None)
        self.assertEqual(updates[1]["context"]["source"], "test_updates function again")

        self.assertLess(data.init_timestamp, updates[0]["timestamp"])
        self.assertLess(updates[0]["timestamp"], updates[1]["timestamp"])

        third_update_context_data = {
            "source": "test_updates function once again",
            "user_id": "42"
        }

        data.register_context(third_update_context_data)
        data.register_update("new_field.2", "xyz", "XYZ")
        new_updates = data.get_new_updates()
        self.assertEqual(len(new_updates), 1)
        self.assertEqual(new_updates[0]["field"], "new_field.2")
        self.assertEqual(new_updates[0]["old_value"], "xyz")
        self.assertEqual(new_updates[0]["new_value"], "XYZ")
        self.assertEqual(new_updates[0]["action"], None)
        self.assertEqual(new_updates[0]["context"]["source"], "test_updates function once again")

        self.assertLess(updates[1]["timestamp"], new_updates[0]["timestamp"])

        test_context_data_for_actions = {
            "source": "test_updates for actions",
            "user_id": "42"
        }

        data.register_context(test_context_data_for_actions)
        data.register_update_action("new_field.3", {"a":"b"})
        act_updates = data.get_new_updates()
        self.assertEqual(len(act_updates), 1)
        self.assertEqual(act_updates[0]["field"], "new_field.3")
        self.assertEqual(act_updates[0]["old_value"], None)
        self.assertEqual(act_updates[0]["new_value"], None)
        self.assertEqual(act_updates[0]["action"], {"a":"b"})
        self.assertEqual(act_updates[0]["context"]["source"], "test_updates for actions")

        self.assertLess(new_updates[0]["timestamp"], act_updates[0]["timestamp"])

    ##-------------------------------------------------------------------------------------------##

if __name__ == '__main__':
    unittest.main()
