from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.service_access.utilities.errors import RecInputError
from common.service_access.utilities.rec_helpers import make_rec_from_field_and_value, set_rec_field
from common.utilities.inversion_of_control import dependencies, Dependency
import mox


__author__ = 'vgold'


class RecHelperTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(RecHelperTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Create caller context
        self.context = {
            "user_id": 1,
            "source": "test_rec_helpers.py"
        }

    def doCleanups(self):

        super(RecHelperTests, self).doCleanups()
        dependencies.clear()

    def test_make_rec_from_field_and_value(self):

        field = "1.2.3.4"
        value = [[1], [2], [3], [4]]

        rec = make_rec_from_field_and_value(field, value)

        expected_rec = {
            "1": {
                "2": {
                    "3": {
                        "4": [[1], [2], [3], [4]]
                    }
                }
            }
        }

        self.assertDictEqual(rec, expected_rec)
    
    def test_set_ref_field(self):
        
        rec = {
            "1": {}
        }
        
        with self.assertRaises(RecInputError):
            set_rec_field(rec, "1.2.3", 4)

        set_rec_field(rec, "1.2.3", 4, error_if_absent=False, upsert=True)

        expected_rec = {
            "1": {
                "2": {
                    "3": 4
                }
            }
        }

        self.assertDictEqual(rec, expected_rec)