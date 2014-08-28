import json
import os
import pprint
import unittest


__author__ = 'imashhor'


class TestValidateDefaultCalcs(unittest.TestCase):

    def setUp(self):
        pass

    def doCleanups(self):
        pass

    def test_validate_default_calcs(self):

        source_root = os.path.dirname(os.path.realpath(__file__)).rsplit("/", 5)[0]

        engines_path = os.path.join(source_root,
                                    "core/service/svc_analytics/implementation/calc/engines")
        ref_data_file = os.path.join(source_root,
                                     "core/common/business_logic/data/analytics_reference_data.json")

        default_calcs_dict = {}

        for item in os.listdir(engines_path):
            dir_path = os.path.join(engines_path, item)
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                default_calcs_filename = os.path.join(dir_path, "default_%s_calcs.json" % item)
                with open(default_calcs_filename, 'r') as fin:
                    default_calcs_dict = dict(default_calcs_dict, **json.load(fin))

        with open(ref_data_file, 'r') as ref:
            ref_data_dict = json.load(ref)

        invalid_calcs = []

        for calc_name, calc_def in default_calcs_dict.iteritems():

            if calc_def["input"]:
                calc_input_fields = [field for field in calc_def["input"]["fields"] if field.startswith("data.analytics")]

                missing_fields = []
                for input_field in calc_input_fields:

                    # Find out if this input field has a corresponding output field resulting from a calculation
                    is_dependency_calculated = False
                    for inner_calc_name, inner_calc_def in default_calcs_dict.iteritems():
                        if "output" in inner_calc_def and inner_calc_def["output"] and self._match_field(input_field, inner_calc_def["output"]["key"]):
                            is_dependency_calculated = True
                        elif "multi_outputs" in inner_calc_def:
                            for output in inner_calc_def["multi_outputs"]:
                                if self._match_field(input_field, output["key"]):
                                    is_dependency_calculated = True

                    if not is_dependency_calculated:
                        missing_fields.append(input_field)

                if missing_fields:
                    invalid_calcs.append({
                        "name": calc_name,
                        "missing input fields": missing_fields
                    })

                # make sure the file is there
                calc_module_path = os.path.join(engines_path, calc_def["engine"], calc_def["engine_module"]+".py")
                if not os.path.exists(calc_module_path):
                    invalid_calcs.append({
                        "name": calc_name,
                        "module not found": calc_module_path
                    })

                # make sure the ref data is complete & accurate
                if calc_def["engine"] not in ref_data_dict["engines"]:
                    invalid_calcs.append({
                        "name": calc_name,
                        "engine not in ref data": calc_def["engine"]
                    })
                if calc_def["engine_module"] not in ref_data_dict["engines"].get(calc_def["engine"], {}):
                    invalid_calcs.append({
                        "name": calc_name,
                        "engine_module not in ref data": calc_def["engine_module"]
                    })


        # Lets just print this list so that people actually know which fields are the problem
        if invalid_calcs:
            pprint.pprint(invalid_calcs)

        self.assertEqual([],invalid_calcs)

    def _match_field(self, input_field, output_field):

        if input_field == output_field:
            return True

        # Handle cases where previous calc inputs one field up (.total, etc.)
        elif input_field.rsplit(".", 1)[0] == output_field:
            return True

        # Handle cases where previous calc inputs two fields up (.raw.total, etc.)
        elif input_field.rsplit(".", 2)[0] == output_field:
            return True

        return False


if __name__ == '__main__':
    unittest.main()




