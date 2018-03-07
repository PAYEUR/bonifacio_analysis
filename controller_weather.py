# -*- coding: utf-8 -*-
from datetime import date
from weather_parsing import model as mp_model


month_dict = {1: 'janvier',
              2: 'fevrier',
              3: 'mars',
              4: 'avril',
              5: 'mai',
              10: 'octobre',
              11: 'novembre',
              12: 'decembre',
              }

date = date(year=2016, month=11, day=3)

if date.day == 1:
    day_string = '1er'
else:
    day_string = str(date.day)

year_string = str(date.year)
month_string = month_dict[date.month]

start_url_string = 'http://www.infoclimat.fr/observations-meteo/archives'
end_url_string = 'bonifacio-cap-pertusato/07770.html'

url = f"{start_url_string}/{day_string}/{month_string}/{year_string}/{end_url_string}"

#with urllib.request.urlopen(url) as f:
with open('tests/test.html', 'r') as f:
    wp = mp_model.WeatherParser(f)
    print(wp.time_slots_spans)
    print(wp.time_slots)
