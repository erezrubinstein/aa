# coding=utf-8
import traceback
import unittest
from multiprocessing import Process, Manager
from common.utilities.multi_process_manager import MultiProcessManager, MultiProcessException
import sys

__author__ = 'imashhor'


class MultiProcessManagerTest(unittest.TestCase):

    def test_run_mapped_process(self):

        def add(a, b, lock):
            with lock:
                return a + b

        manager = MultiProcessManager()

        manager.run_mapped_processes(add, [ [1,2], [3,4], [5,6] ])

        self.assertListEqual([3,7,11], manager.results)

    def test_run_mapped_process__raise_exception(self):

        def add(a, b, lock):
            # Bad code
            return a[0] + b[0]

        manager = MultiProcessManager()

        with self.assertRaises(MultiProcessException):
            manager.run_mapped_processes(add, [ [1,2], [3,4], [5,6] ])


    def test_add_process__result_and_error_collection(self):

        def fail_function():
            raise Exception("wargh")

        def pass_function():
            return 10

        manager = MultiProcessManager()

        manager.add_process(fail_function)
        manager.add_process(pass_function)
        manager.add_process(pass_function)
        manager.add_process(fail_function)

        manager.start_all()
        manager.join_all()

        # Verify results array
        self.assertListEqual([None, 10, 10, None], manager.results)

        # Verity individual failed results array
        # self.assertRegexpMatches("", manager.error_results[0])
        self.assertTrue(manager.error_results[0].startswith("Traceback (most recent call last):\n"))
        self.assertIsNone(manager.error_results[1])
        self.assertIsNone(manager.error_results[2])
        self.assertTrue(manager.error_results[3].startswith("Traceback (most recent call last):\n"))


    def test_add_process__parameter_passing(self):
        def one_param(one):
            return one

        def three_params(one, two, three):
            return [one, two, three]

        manager = MultiProcessManager()

        manager.add_process(one_param, "hello")
        manager.add_process(three_params, "my", "name", "is")

        manager.start_all()
        manager.join_all()

        # Verify results
        self.assertEqual("hello", manager.results[0])
        self.assertEqual(["my", "name", "is"], manager.results[1])
        self.assertListEqual([None, None], manager.error_results)


    def test_add_process_with_lock(self):
        """
        If the lock is not passed, there would be error results
        """

        def one_param(one, lock):
            with lock:
                return one

        def three_params(one, two, three, lock):
            with lock:
                return [one, two, three]

        manager = MultiProcessManager()

        manager.add_process_with_lock(one_param, "hello")
        manager.add_process_with_lock(three_params, "my", "name", "is")

        manager.start_all()
        manager.join_all()

        # Verify results
        self.assertListEqual([None, None], manager.error_results)
        self.assertEqual("hello", manager.results[0])
        self.assertEqual(["my", "name", "is"], manager.results[1])


    def test_add_mapped_processes(self):
        def add(a, b):
            return a + b

        manager = MultiProcessManager()
        manager.add_mapped_processes(add, [[1, 2], [11, 22], [2.5, 1.2]])

        manager.start_all()
        manager.join_all()

        # Verify results
        self.assertListEqual([None, None, None], manager.error_results)
        self.assertListEqual([3, 33, 3.7], manager.results)


    def test_add_mapped_processes__no_sublist(self):
        def double(a):
            return a + a

        manager = MultiProcessManager()
        manager.add_mapped_processes(double, [2, 3, 4])

        manager.start_all()
        manager.join_all()

        # Verify results
        self.assertListEqual([None, None, None], manager.error_results)
        self.assertListEqual([4, 6, 8], manager.results)


    def test_add_mapped_processes_with_lock(self):
        def add(a, b, lock):
            with lock:
                return a + b

        def double(a, lock):
            with lock:
                return a + a

        manager = MultiProcessManager()
        manager.add_mapped_processes_with_lock(add, [[1, 2], [11, 22]])
        manager.add_mapped_processes_with_lock(double, [4, 6])

        manager.start_all()
        manager.join_all()

        # Verify results
        self.assertListEqual([None, None, None, None], manager.error_results)
        self.assertListEqual([3, 33, 8, 12], manager.results)


if __name__ == '__main__':
    unittest.main()





