from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from common.utilities.lox import Lox
from bson.objectid import ObjectId
import datetime


__author__ = 'erezrubinstein'


class LoxTestCollection(ServiceTestCollection):

    def initialize(self):

        # get params builder
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        # context
        self._context = {
            "user_id": ObjectId(),
            "source": "white_space_analytics_integration_tests"
        }

    def setUp(self):

        self.mds_access.call_delete_reset_database()


    # ---------------------------- Begin Tests ---------------------------- #

    def test_locks(self):

        lock_type = "BagelLock"
        lock_ids = [1, 2, 3, 4]

        # get locks for these ids
        with Lox(lock_type, lock_ids, (self.context,)):

            # get a lock for one of them, and verify that it raises an exception
            self.test_case.assertRaises(Exception, Lox(lock_type, 1, (self.context,)).__enter__)

        # make sure I can lock the one that had an error out after the last one finished
        with Lox(lock_type, 1, (self.context,)):
            pass



    def test_locks_keep_alive(self):

        lock_type = "BagelLock"
        lock_ids = [1]

        # insert a lox object with an up-to-date keep alive flag
        entities = [
            {
                "name": "whatever",
                "data": {
                    "lock_type": lock_type,
                    "lock_id": 1,
                    "is_locked": True,
                    "keep_alive": datetime.datetime.utcnow()
                }
            }
        ]
        self.main_access.mds.call_batch_insert_entities("lox", entities, self._context)

        # make sure we get an error
        self.test_case.assertRaises(Exception, Lox(lock_type, lock_ids, (self.context,)).__enter__)

        # update the keep alive to more than 10 minutes ago
        old_keep_alive = datetime.datetime.utcnow() - datetime.timedelta(minutes = 10)
        query = { "data.lock_type": lock_type, "data.lock_id": 1 }
        update = { "$set": { "data.keep_alive": old_keep_alive }}
        self.mds_access.call_batch_update_entities("lox", query, update, self.context)

        # should work now, because the keep alive is dead
        with Lox(lock_type, lock_ids, (self.context,)):
            pass