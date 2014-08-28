from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.utilities.helpers import generate_id
from core.service.svc_analytics.implementation.calc.calc import Calc
import unittest
import mox


__author__ = 'jsternberg'


class CalcTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(CalcTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        self.cfg = "bah"
        self.logger = Dependency("FlaskLogger").value
        self.calc_id = generate_id()
        self.name = "coal"
        self.description = "chugga chugga"
        self.engine = "steam"
        self.engine_module = "coal.power.steam.punk"
        self.input = {
            "target_entity_field": "asdf"
        }
        self.output = {
            "key": "data.analytics.42",
            "target_entity_type": "woot"
        }
        self.context_data = {"stuff": True}

    def doCleanups(self):

        super(CalcTests, self).doCleanups()
        dependencies.clear()

    def test_dict_init(self):

        calc_rec = {
            "_id": self.calc_id,
            "name": self.name,
            "description": self.description,
            "engine": self.engine,
            "engine_module": self.engine_module,
            "input": self.input,
            "output": self.output,
            "context_data": self.context_data
        }

        calc = Calc.dict_init(self.cfg, self.logger, calc_rec)

        self.__assert_calc_attributes(calc)

    def test_to_dict(self):

        calc_rec = {
            "_id": self.calc_id,
            "name": self.name,
            "description": self.description,
            "engine": self.engine,
            "engine_module": self.engine_module,
            "input": self.input,
            "output": self.output,
            "context_data": self.context_data
        }

        calc = Calc.dict_init(self.cfg, self.logger, calc_rec)

        self.assertDictContainsSubset(calc_rec, calc.to_dict())

    def test_start(self):

        calc_rec = {
            "_id": self.calc_id,
            "name": self.name,
            "description": self.description,
            "engine": self.engine,
            "engine_module": self.engine_module,
            "input": self.input,
            "output": self.output,
            "context_data": self.context_data
        }

        calc = Calc.dict_init(self.cfg, self.logger, calc_rec)

        # calc.start()

    #----------------------# Private Methods #----------------------#

    def __assert_calc_attributes(self, calc):

        self.assertEqual(calc.cfg, self.cfg)
        self.assertEqual(calc.logger, self.logger)
        self.assertEqual(calc.calc_id, self.calc_id)
        self.assertEqual(calc.name, self.name)
        self.assertEqual(calc.description, self.description)
        self.assertEqual(calc.engine, self.engine)
        self.assertEqual(calc.engine_module, self.engine_module)
        self.assertEqual(calc.input, self.input)
        self.assertEqual(calc.output, self.output)
        self.assertEqual(calc.context_data, self.context_data)


if __name__ == '__main__':
    unittest.main()