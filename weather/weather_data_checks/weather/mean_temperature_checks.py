from core.data_checks.implementation.company_checks.weather.mean_temperature_check_base import MeanTemperatureCheckBase

__author__ = 'jsternberg'

class MeanTempCelsiusCheck(MeanTemperatureCheckBase):

    def check(self):
        self.units = "c"
        return super(MeanTempCelsiusCheck, self).check()

class MeanTempFahrenheitCheck(MeanTemperatureCheckBase):

    def check(self):
        self.units = "f"
        return super(MeanTempFahrenheitCheck, self).check()
