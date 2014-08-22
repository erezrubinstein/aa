

class DataCheck(object):
    def __init__(self):
        self.data_check_id = None
        self.data_check_type_id = None
        self.check_done = None
        self.data_check_values = []
        self.bad_data_rows = None


##################################################### Factory Methods ###########################################################################
    @classmethod
    def standard_init(cls, data_check_id, data_check_type_id, check_done, bad_data_rows):
        data_check = DataCheck()
        data_check.data_check_id = data_check_id
        data_check.data_check_type_id = data_check_type_id
        data_check.check_done = check_done
        data_check.bad_data_rows = bad_data_rows
        return data_check

    @classmethod
    def pre_init(cls, data_check_type_id):
        data_check = DataCheck()
        data_check.data_check_type_id = data_check_type_id
        data_check.data_check_values = []
        return data_check


############################################# Descriptor Methods ################################################
    def __eq__(self, other):
        # compares 2 data_check objects, but does NOT include check_done
        return self.data_check_id == other.data_check_id and self.data_check_type_id == other.data_check_type_id and\
               self.bad_data_rows == other.bad_data_rows and len(self.data_check_values) == len(other.data_check_values) and\
                set(self.data_check_values) == set(other.data_check_values)








class DataCheckValue(object):
    def __init__(self):
        self.data_check_value_id = None
        self.data_check_id = None
        self.value_type = None
        self.expected_value = None
        self.actual_value = None
        self.entity_id = None


##################################################### Factory Methods ###########################################################################
    @classmethod
    def standard_init(cls, data_check_value_id, data_check_id, value_type, expected_value, actual_value, entity_id):
        data_check_value = DataCheckValue()
        data_check_value.data_check_value_id = data_check_value_id
        data_check_value.data_check_id = data_check_id
        data_check_value.value_type = value_type
        data_check_value.expected_value = expected_value
        data_check_value.actual_value = actual_value
        data_check_value.entity_id = entity_id
        return data_check_value

    @classmethod
    def pre_init(cls, value_type, expected_value, actual_value, entity_id):
        data_check_value = DataCheckValue()
        #data_check_value.data_check_id = data_check_id
        data_check_value.value_type = value_type
        data_check_value.expected_value = expected_value
        data_check_value.actual_value = actual_value
        data_check_value.entity_id = entity_id
        return data_check_value

############################################# Descriptor Methods ################################################
    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        # does NOT include data_check_value_id, data_check_id will cover that
        # since it is the foreign key
        return hash((self.data_check_id, self.value_type, self.expected_value, self.actual_value, self.entity_id))








class DataCheckType(object):
    def __init__(self):
        self.data_check_type_id = None
        self.name = None
        self.entity_type_id = None
        self.sql = None
        self.severity_level = None
        self.fail_threshold = None


##################################################### Factory Methods ##################################################
    @classmethod
    def standard_init(cls, data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold):
        data_check_type = DataCheckType()
        data_check_type.data_check_type_id = data_check_type_id
        data_check_type.name = name
        data_check_type.entity_type_id = entity_type_id
        data_check_type.sql = sql
        data_check_type.severity_level = severity_level
        data_check_type.fail_threshold = fail_threshold
        return data_check_type


############################################# Descriptor Methods ################################################
    def __eq__(self, other):
        return self.data_check_type_id == other.data_check_type_id and self.name == other.name and \
            self.entity_type_id == other.entity_type_id and self.sql == other.sql and \
            self.severity_level == other.severity_level and self.fail_threshold == other.fail_threshold
