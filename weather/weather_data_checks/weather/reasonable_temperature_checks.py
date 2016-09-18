from core.data_checks.implementation.company_checks.weather.reasonable_weather_check_base import ReasonableWeatherCheckBase

__author__ = 'jsternberg'

"""
http://en.wikipedia.org/wiki/List_of_weather_records
"""
MIN_C = -66.1
MAX_C = 56.7
MIN_F = -87.0
MAX_F = 134


class ReasonableMinTempCelsiusCheck(ReasonableWeatherCheckBase):

    def check(self):
        self.field = "tcmin"
        self.description = "min temperature (c)"
        self.valid_min = MIN_C
        self.valid_max = MAX_C
        return super(ReasonableMinTempCelsiusCheck, self).check()


class ReasonableMaxTempCelsiusCheck(ReasonableWeatherCheckBase):

    def check(self):
        self.field = "tcmax"
        self.description = "max temperature (c)"
        self.valid_min = MIN_C
        self.valid_max = MAX_C
        return super(ReasonableMaxTempCelsiusCheck, self).check()


class ReasonableMinTempFahrenheitCheck(ReasonableWeatherCheckBase):

    def check(self):
        self.field = "tfmin"
        self.description = "min temperature (f)"
        self.valid_min = MIN_F
        self.valid_max = MAX_F
        return super(ReasonableMinTempFahrenheitCheck, self).check()


class ReasonableMaxTempFahrenheitCheck(ReasonableWeatherCheckBase):

    def check(self):
        self.field = "tfmax"
        self.description = "max temperature (f)"
        self.valid_min = MIN_F
        self.valid_max = MAX_F
        return super(ReasonableMaxTempFahrenheitCheck, self).check()