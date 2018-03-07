# -*- coding: utf-8 -*-
from datetime import date

from weather_parsing import model as mp_model

date = date(year=2016, month=11, day=3)


wp = mp_model.WeatherParser(date)
print(wp.wind_list)
