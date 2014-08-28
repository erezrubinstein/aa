
__author__ = 'vgold'


class MockMongoAccess(object):

    methods_to_ignore = ["init_collections", "ensure_index", "drop", "drop_collections"]
    methods_to_record = ["insert", "update", "remove", "find", "find_one"]

    def __init__(self):
        self.__return_list = []
        self.__records = []
        self.__record_method_name = None

    #------------------------# Public Interface #------------------------#

    def append_to_return_queue(self, item):
        self.__return_list.append(item)

    def pop_return_queue(self, *args, **kwargs):
        return self.__return_list.pop(0) if len(self.__return_list) > 0 else None

    def get_recorded_calls(self):
        return self.__records[:]

    def clear_recorded_calls(self):
        self.__records = []

    #------------------------# Auto-magic #------------------------#

    def __getattr__(self, item):
        """
        Return name of attribute to call
        """
        if item in self.methods_to_ignore:
            return self.__getattribute__("catch_all")

        elif item in self.methods_to_record:
            self.__record_method_name = item
            return self.__getattribute__("record")

        else:
            return self.__getattribute__("pop_return_queue")

    def catch_all(self, *args, **kwargs):
        return None

    def record(self, *args, **kwargs):
        self.__records.append({"method": self.__record_method_name, "args": args, "kwargs": kwargs})
        self.__record_method_name = None
        return self.pop_return_queue(*args, **kwargs)


