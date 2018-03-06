# -*- coding: utf-8 -*-
import urllib.request
from datetime import date, timedelta
from bs4 import BeautifulSoup

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


class WeatherParser:

    def __init__(self,
                 url_or_file_object):

        self.url_or_file_object = url_or_file_object
        self.soup = BeautifulSoup(url, 'lxml')
        self.temp_spans = self.get_temp_spans()
        self.wind_spans = self.get_wind_spans()
        self.temp_list = [float(elt.text) for elt in self.temp_spans]
        self.wind_list = [float(elt.text) for elt in self.wind_spans[::2]]
        self.wind_gust_list = [float(elt.text) for elt in self.wind_spans[1::2]]

    def get_temp_spans(self):
        sp = self.soup.find_all('span',
                                attrs={'style': 'font-weight:bold;margin-top:10px;display:inline-block;font-size:16px'}
                                )
        return sp

    def get_wind_spans(self):
        return self.soup.find_all('span', attrs={'style': 'font-weight:bold'})


#with urllib.request.urlopen(url) as f:
# with open('../tests/test.html', 'r') as f:
#     wp = WeatherParser(f)
#     print(wp.temp_list)
#     print(wp.wind_list)
#     print(wp.wind_gust_list)
