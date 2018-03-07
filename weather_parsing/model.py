# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup


class WeatherParser:

    def __init__(self,
                 url_or_file_object):

        self.url_or_file_object = url_or_file_object
        self.soup = BeautifulSoup(self.url_or_file_object, 'lxml')
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



