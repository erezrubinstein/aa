import glob
import os
import unittest
import mox
import pandas as pd
import numpy as np
import __builtin__
from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from economics.raw_data.monthly_us_labor_data_to_mds import LaborDataReader, LaborToMDSUploader, MonthlyLaborGatheringRunner

__author__ = 'clairseager'

# do a convenient monkey-patch on the DataFrame class.
def dropcols(self, list_of_cols):
    for col in list_of_cols:
        if col in self:
            self = self.drop(col, axis=1)
    return self
pd.DataFrame.dropcols = dropcols

class LaborDataToMDSTest(mox.MoxTestBase):

    def setUp(self):
        super(LaborDataToMDSTest, self).setUp()

        # set up mocks
        register_common_mock_dependencies()
        self.mox.StubOutWithMock(__builtin__, "open")
        self.mox.StubOutWithMock(glob, "glob")
        self.mox.StubOutWithMock(pd, "read_csv")

        # logger
        self.logger = Dependency("SimpleConsole").value

        config = {}
        data_directory = "monty/python"
        email_recipients = "taco@email"
        self.data_reader = LaborDataReader(self.logger, data_directory, rds_file_id="walkinthepark", as_of_date="2013-06-01T00:00:00")
        self.mds_uploader = LaborToMDSUploader(self.logger, self.data_reader, config, "labor")
        self.monthly_runner = MonthlyLaborGatheringRunner(self.logger, config, email_recipients)

        self.mds_uploader.mongo_upload_host = "fakemongohost:27017"

        self.setup_expected_dfs()

    def setup_expected_dfs(self):
        # the lists at the bottom of this file are extremely lazy copy-pastes of a few lines from the real data files.
        # in this method read the text and turn them into a real dataframe that resembles what the read_csv method gets...
        s = [i.split("\t") for i in series_file]
        self.series_df = pd.DataFrame(s[1:], columns=s[0])

        m = [i.split("\t") for i in measure_file]
        self.measure_df = pd.DataFrame(m[1:], columns=m[0])

        a = [i.split("\t") for i in area_file]
        self.area_df = pd.DataFrame(a[1:], columns=a[0]).dropcols(["", "display_level", "selectable", "sort_sequence"])

        a = [i.split("\t") for i in data[0]]
        self.alabama_df = pd.DataFrame(a[1:], columns=a[0])
        self.alabama_df.year = self.alabama_df.year.astype(float)

        a = [i.split("\t") for i in data[1]]
        self.alaska_df = pd.DataFrame(a[1:], columns=a[0])
        self.alaska_df.year = self.alaska_df.year.astype(float)

        self.series = pd.DataFrame.from_dict(cleaned_series)
        self.blsarea = pd.DataFrame.from_dict(cleaned_blsarea)
        self.states = {"Alaska": pd.DataFrame.from_dict(cleaned_states["Alaska"]), "Alabama":pd.DataFrame.from_dict(cleaned_states["Alabama"])}



    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    # ~~~ TEST READER ~~~
    def test_reader__read_all_BLS_data(self):

        f = glob.glob(os.path.join(self.data_reader.data_directory, "la.data*")).AndReturn(["la.data.Alabama", "la.data.Alaska"])

        with open(f[0], 'r').AndReturn(MockFile()) as opened:
            pd.read_csv(opened, sep="\t", usecols=[0,1,2,3,4]).AndReturn(self.alabama_df)
        with open(f[1], 'r').AndReturn(MockFile()) as opened:
            pd.read_csv(opened, sep="\t", usecols=[0,1,2,3,4]).AndReturn(self.alaska_df)

        self.mox.ReplayAll()

        self.data_reader.read_all_BLS_data()

        self.assertEqual(len(self.data_reader.state_data), 2)
        self.assertEqual(len(self.data_reader.state_data["Alabama"]), 5)
        self.assertEqual(len(self.data_reader.state_data["Alaska"]), 5)
        self.assertEqual(self.data_reader.state_data["Alabama"].value.dtype, np.float64)
        self.assertEqual(self.data_reader.state_data["Alaska"].value.dtype, np.float64)
        self.assertEqual(self.data_reader.state_data["Alaska"].ix[3,"value"], 7.3)
        self.assertNotEqual(self.data_reader.state_data["Alaska"].ix[3,"value"], 6.3)
        self.assertTrue(np.isnan(self.data_reader.state_data["Alaska"].ix[4,"value"]))

        expected_columns = ["series_id","year","period","value","footnote_codes"]
        self.assertItemsEqual(self.data_reader.state_data["Alabama"].columns, expected_columns)


    def test_reader__read_BLS_series_file(self):

        with open("monty/python/la.series", 'r').AndReturn(MockFile(series_file)) as f:
            series = pd.read_csv(f, sep="\t", usecols=[0,1,2,3,4]).AndReturn(self.series_df)
        with open("monty/python/la.measure", "r").AndReturn(MockFile(measure_file)) as f:
            measure = pd.read_csv(f, sep="\t").AndReturn(self.measure_df)

        self.mox.ReplayAll()

        self.data_reader.read_BLS_series_file()

        expected_columns = series_file[0].split("\t") + ["measure_text"]
        expected_columns.remove("measure_code")
        self.assertItemsEqual(self.data_reader.series.columns, expected_columns)
        self.assertEqual(len(self.data_reader.series), 3)
        self.assertEqual(self.data_reader.series.ix[0,"measure_text"], "unemployment rate")
        self.assertEqual(self.data_reader.series.ix[1,"measure_text"], "unemployment rate")
        self.assertEqual(self.data_reader.series.ix[2,"measure_text"], "unemployment")

        with self.assertRaises(KeyError) as ex:
            self.data_reader.series.ix[3,"measure_text"]
        self.assertEqual(ex.exception.message, 3)

    def test_reader__read_BLS_area_file(self):

        with open("monty/python/la.area", 'r').AndReturn(MockFile()) as f:
            pd.read_csv(f, sep="\t", usecols=[0,1,2,3,4,5]).AndReturn(self.area_df)

        self.mox.ReplayAll()

        self.data_reader.read_BLS_area_file()

        self.assertEqual(len(self.data_reader.blsarea), 5)

        self.assertItemsEqual(self.data_reader.blsarea.to_dict("list")["area_text"], cleaned_blsarea["area_text"])

        expected_columns = ['area_type_code', 'area_code', 'area_text']
        self.assertItemsEqual(self.data_reader.blsarea.columns, expected_columns)

    def test_uploader__states_into_nation_table(self):
        # let's not run the data_reader but pretend we did.
        self.data_reader.series = self.series
        self.data_reader.blsarea = self.blsarea
        self.data_reader.state_data = self.states

        self.mds_uploader._states_into_nation_table()

        expected_columns = ["series_id","year","period","value","state", "rds_file_id","as_of_date", "area_type_code","area_code","area_text", "measure_text"]
        self.assertItemsEqual(self.mds_uploader.nation.columns, expected_columns)
        self.assertEqual(len(self.mds_uploader.nation), 10)
        self.assertItemsEqual(self.mds_uploader.nation.groupby("state").groups.keys(), ["Alaska","Alabama"])
        self.assertItemsEqual(self.mds_uploader.nation.groupby("period").groups.keys(), ['M01', 'M02', 'M03', 'M04', 'M05'])
        self.assertEqual(len(self.mds_uploader.nation.groupby("value")), 8)
        self.assertEqual(len(self.mds_uploader.nation[self.mds_uploader.nation.value.isnull()]), 2)




class MockFile():
    def __init__(self, give_back=None):
        self.echo = give_back
    def __enter__(self):
        return self.echo

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


data = [
           ["series_id	year	period	value	footnote_codes",
            "LASST22000003    	2012	M01	         6.0	",
            "LASST22000003    	2012	M02	         6.1	",
            "LASST22000003    	2012	M03	         6.2	",
            "LASST22000003    	2012	M04	         6.3	",
            "LASST22000003    	2012	M05	         -	N"
           ],
           ["series_id	year	period	value	footnote_codes",
            "LASST22000013    	2012	M01	         7.0	",
            "LASST22000013    	2012	M02	         7.1	",
            "LASST22000013    	2012	M03	         7.2	",
            "LASST22000013    	2012	M04	         7.3	",
            "LASST22000013    	2012	M05	         -	N"
           ]
]

series_file = [
    "series_id	area_type_code	area_code	measure_code	seasonal	srd_code	footnote_codes	begin_year	begin_period	end_year	end_period",
    "LASST22000003    	G	BS060100	03	U	06		2012	M01	2013	M07",
    "LASST22000004    	G	BS060100	04	U	06		2012	M01	2013	M07",
    "LASST22000005    	G	BS060100	05	S	06		2012	M01	2013	M07",
    "LASST22000006    	G	BS060100	06	S	06		2012	M01	2013	M07",
    "LASST22000013    	G	CN020200	03	U	06		2012	M01	2013	M07",
]

measure_file = [
    "measure_code	measure_text",
    "03	unemployment rate",
    "04	unemployment",
    "05	employment",
    "06	labor force"
]

area_file = [
    "area_type_code	area_code	area_text	display_level	selectable	sort_sequence	",
    "G	BS060100	Spring Valley village, NY	00	T	5199	    ",
    "F	CN020200	Anchorage Borough/municipality, AK	00	T	149	    ",
    "G	CN020200	Anchorage Borough/municipality, AK	00	T	179	    ",
    "F	PS060900	San Francisco County/city, CA	00	T	450	    ",
    "G	PS060900	San Francisco County/city, CA	00	T	677	    "
]

cleaned_states = {
    "Alabama": {
        'series_id': ['LASST22000003    ', 'LASST22000003    ', 'LASST22000003    ', 'LASST22000003    ', 'LASST22000003    '],
        'period': ['M01', 'M02', 'M03', 'M04', 'M05'],
        'value': [6.0, 6.1, 6.2, 6.3, np.nan],
        'year': ['2012', '2012', '2012', '2012', '2012']
    },
    "Alaska": {
        'series_id': ['LASST22000013    ', 'LASST22000013    ', 'LASST22000013    ', 'LASST22000013    ', 'LASST22000013    '],
        'period': ['M01', 'M02', 'M03', 'M04', 'M05'],
        'value': [7.0, 7.1, 7.2, 7.3, np.nan],
        'year': ['2012', '2012', '2012', '2012', '2012']
    }
}

cleaned_series = {
    'series_id': ['LASST22000003    ', 'LASST22000013    ', 'LASST22000004    '],
    'area_type_code': ['G', 'G', 'G'],
    'area_code': ['BS060100', 'CN020200', 'BS060100'],
    'seasonal': ['U', 'U', 'U'],
    'measure_text': ['unemployment rate', 'unemployment rate', 'unemployment']
}

cleaned_blsarea = {
    'area_code': ['BS060100', 'CN020200', 'CN020200', 'PS060900', 'PS060900'],
    'area_text': ['Spring Valley village, NY', 'Anchorage Borough, AK', 'Anchorage municipality, AK', 'San Francisco County, CA', 'San Francisco city, CA'],
    'area_type_code': ['G', 'F', 'G', 'F', 'G']
}



if __name__ == '__main__':
    unittest.main()
