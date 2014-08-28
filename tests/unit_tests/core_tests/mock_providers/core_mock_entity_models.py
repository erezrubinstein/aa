import uuid

__author__ = "vgold"


class MockEntityManager(object):

    def __init__(self):
        self.__documents = []

    def find(self, **kwargs):
        temp = None
        for obj in self.__documents:
            temp = obj.match(**kwargs)
            if temp:
                break
        return temp

    def find_all(self, **kwargs):
        results = []
        for obj in self.__documents:
            temp = obj.match(**kwargs)
            if temp:
                results.append(temp)
        return results

    def save(self, record):
        record_index = None
        for i, rec in enumerate(self.__documents):
            if rec == record:
                record_index = i
                break

        if record_index is not None:
            self.__documents[record_index] = record
        else:
            self.__documents.append(record)
        return self

    def delete(self, record):
        self.__documents = [rec for rec in self.__documents if rec != record]
        return True


class MockEntity(object):

    @classmethod
    def find(cls, **kwargs):
        return cls._manager.find(**kwargs)

    @classmethod
    def find_all(cls, **kwargs):
        return cls._manager.find_all(**kwargs)

    def create(self, **kwargs):
        self.id = uuid.uuid4()
        for field in self.fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])
            elif field != "id":
                # print kwargs, field
                raise Exception("Missing key for %s model." % self.__class__.__name__)

    def save(self):
        self._manager.save(self)
        return self

    def update(self, **kwargs):
        for k, v in kwargs.iteritems():
            if k != 'id' and hasattr(self, k):
                setattr(self, k, v)
        self._manager.save(self)
        return self

    def delete(self):
        return self._manager.delete(self)

    def match(self, **kwargs):
        match = True
        for k, v in kwargs.iteritems():
            if not hasattr(self, k) or getattr(self, k) != v:
                match = False
        return self if match else None

    def serialize(self):
        return {field: getattr(self, field) for field in self.fields}


class MockUser(MockEntity):

    _manager = MockEntityManager()

    def __init__(self, **kwargs):
        self.fields = ["id", "email", "password", "salt", "active", "confirmed_at", "is_generalist", "roles"]
        self.create(**kwargs)

    def serialize(self):
        return {field: getattr(self, field) for field in self.fields}


class MockRole(MockEntity):

    _manager = MockEntityManager()

    def __init__(self, **kwargs):
        self.fields = ["id", "name", "description"]
        self.create(**kwargs)


class MockTeam(MockEntity):

    _manager = MockEntityManager()

    def __init__(self, **kwargs):
        self.fields = ["id", "name", "description", "is_generalist"]
        self.create(**kwargs)


class MockUserTeam(MockEntity):

    _manager = MockEntityManager()

    def __init__(self, **kwargs):
        self.fields = ["id", "user_id", "team_id"]
        self.create(**kwargs)


class MockTeamIndustry(MockEntity):

    _manager = MockEntityManager()

    def __init__(self, **kwargs):
        self.fields = ["id", "team_id", "industry_id"]
        self.create(**kwargs)