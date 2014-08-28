from collections import OrderedDict


class MockMDSParamsBuilder(object):
    def create_params(self, **kwargs):
        params = {
            'params': str([[key, kwargs[key]] for key in sorted(kwargs.iterkeys())])
        }
        return params