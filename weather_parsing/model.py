# -*- coding: utf-8 -*-
import re
import urllib.request

from bs4 import BeautifulSoup

MONTH_DICT = {1: 'janvier',
              2: 'fevrier',
              3: 'mars',
              4: 'avril',
              5: 'mai',
              10: 'octobre',
              11: 'novembre',
              12: 'decembre',
              }


class WeatherParser:

    def __init__(self, date):

        self.date = date
        self.url = self.create_url()
        self._soup = BeautifulSoup(self.get_readable_object(), 'lxml')
        self._temp_spans = self.get_temp_spans()
        self._wind_spans = self.get_wind_spans()
        self._time_slots_spans = self.get_time_slots_spans()
        self.temp_list = [float(elt.text) for elt in self._temp_spans]
        self.wind_list = [float(elt.text) for elt in self._wind_spans[::2]]
        self.wind_gust_list = [float(elt.text) for elt in self._wind_spans[1::2]]
        self.time_slots_list = [float(elt.text.split('h')[0]) for elt in self._time_slots_spans]
        self.rain_list = self.get_rain_list()

    def get_readable_object(self):
        return urllib.request.urlopen(self.url)

    def create_url(self):

        date = self.date

        if date.day == 1:
            day_string = '1er'
        else:
            day_string = str(date.day)

        year_string = str(date.year)
        month_string = MONTH_DICT[date.month]

        start_url_string = 'http://www.infoclimat.fr/observations-meteo/archives'
        end_url_string = 'bonifacio-cap-pertusato/07770.html'

        url = f"{start_url_string}/{day_string}/{month_string}/{year_string}/{end_url_string}"

        return url

    def get_temp_spans(self):
        sp = self._soup.find_all('span',
                                 attrs={'style': 'font-weight:bold;margin-top:10px;display:inline-block;font-size:16px'}
                                 )
        return sp

    def get_wind_spans(self):
        return self._soup.find_all('span', attrs={'style': 'font-weight:bold'})

    def get_time_slots_spans(self):
        sp = self._soup.find_all('span', attrs={'class': 'tipsy-trigger',
                                                'title': re.compile('Heure*')
                                                })
        return sp

    def get_rain_list(self):
        return [float(elt.parent.text.split()[0]) for elt in self._soup.find_all('span', string='mm/1h')]
