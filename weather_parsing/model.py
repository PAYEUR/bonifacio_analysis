# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re


class WeatherParser:

    def __init__(self,
                 url_or_file_object):

        self.url_or_file_object = url_or_file_object
        self.soup = BeautifulSoup(self.url_or_file_object, 'lxml')
        self.temp_spans = self.get_temp_spans()
        self.wind_spans = self.get_wind_spans()
        self.time_slots_spans = self.get_time_slots_spans()
        self.temp_list = [float(elt.text) for elt in self.temp_spans]
        self.wind_list = [float(elt.text) for elt in self.wind_spans[::2]]
        self.wind_gust_list = [float(elt.text) for elt in self.wind_spans[1::2]]
        self.time_slots_list = [float(elt.text.split('h')[0]) for elt in self.time_slots_spans]

    def get_temp_spans(self):
        sp = self.soup.find_all('span',
                                attrs={'style': 'font-weight:bold;margin-top:10px;display:inline-block;font-size:16px'}
                                )
        return sp

    def get_wind_spans(self):
        return self.soup.find_all('span', attrs={'style': 'font-weight:bold'})

    def get_time_slots_spans(self):
        sp = self.soup.find_all('span', attrs={'class': 'tipsy-trigger',
                                               'title': re.compile('Heure*')
                                               })
        return sp

    def get_water_spans(self):
        sp_list = self.soup.find_all('td', attrs={'style': 'background-color:rgba(0,0,0,0.1)'})
        return sp_list