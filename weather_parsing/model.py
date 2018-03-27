# -*- coding: utf-8 -*-
import re
import time
import datetime
import random
import pickle
import itertools
from urllib import request, error

import numpy as np
from bs4 import BeautifulSoup

from root import root

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
        return request.urlopen(self.url)

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


class WeatherParserManager:

    def __init__(self, start_time, end_time, month_name):
        self.start_time = start_time
        self.end_time = end_time
        self.month_name = month_name

    @property
    def date_list(self):
        date = self.start_time.date()
        date_list = [date]
        while date < self.end_time.date():
            date += datetime.timedelta(days=1)
            date_list.append(date)
        return date_list

    @property
    def data_file_name(self):
        return root/f"weather_parsing/weather_data/{self.month_name}.weather"

    def save_weather_parser(self):

        date_list = self.date_list
        file_name = self.data_file_name

        # get weather_parsers from Http request
        data = {}
        for date in date_list:
            print('connexion')
            time.sleep(random.uniform(1, 2))
            try:
                wp = WeatherParser(date)
            except error.HTTPError:
                time.sleep(random.uniform(5, 10))
                try:
                    wp = WeatherParser(date)
                except error.HTTPError:
                    print('Waiting a bit more')
                    time.sleep(random.uniform(20, 30))
                    wp = WeatherParser(date)
            finally:
                data[date, 'temp'] = wp.temp_list
                data[date, 'wind'] = wp.wind_list
                data[date, 'wind_gust'] = wp.wind_gust_list
                data[date, 'rain'] = wp.rain_list

        # open weather parser under file_name as dict(key=date, value=weather_parser)
        with open(file_name, 'wb') as f:
            pickle.dump(data, f)

    def read_weather_parser_file(self):

        date_list = self.date_list
        data_file_name = self.data_file_name
        with open(data_file_name, 'rb') as f:
            data = pickle.load(f)

            wind = list(itertools.chain(*[data[date, 'wind'] for date in date_list]))
            rain = list(itertools.chain(*[data[date, 'rain'] for date in date_list]))
            wind_gust = list(itertools.chain(*[data[date, 'wind_gust'] for date in date_list]))
            temp = list(itertools.chain(*[data[date, 'temp'] for date in date_list]))

        return wind, wind_gust, temp, rain

    def get_weather_data(self):

        try:
            wind, wind_gust, temp, rain = self.read_weather_parser_file()
        except FileNotFoundError:
            self.save_weather_parser()
            print('data saved')
            wind, wind_gust, temp, rain = self.read_weather_parser_file()
        return wind, wind_gust, temp, rain


def create_x_abscissa(datetime_list, weather_data):
    if len(datetime_list) == len(weather_data):
        return np.arange(len(datetime_list))
    else:
        print(f'Length of weather array is {len(weather_data)}, {len(datetime_list)} was expected')
        return np.arange(len(weather_data))
