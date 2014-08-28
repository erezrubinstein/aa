from tests.unit_tests.core_tests.mock_providers.mock_mds_access import MockMDSAccess
from tests.unit_tests.core_tests.mock_providers.mock_rds_access import MockRDSAccess


class MockMainAccess(object):
    def __init__(self):
        self.mds = MockMDSAccess()
        self.rds = MockRDSAccess()