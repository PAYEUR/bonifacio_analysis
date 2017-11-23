# -*- coding: utf-8 -*-
import unittest
import numpy as np
from obspy import read
import collect_data.model as model
from obspy.core.stream import Stream
from datetime import datetime, timedelta
import pytest


class ModelTest(unittest.TestCase):

    def setUp(self):
        self.file1 = 'data_test/2016.10.23-08.13.49.REF.C00.SAC'
        self.file2 = 'data_test/2016.10.23-08.13.49.REF.C01.SAC'
        self.file_path = 'data_test/2016.10.23-08.13.49.REF.'
        self.mother_repository = 'data_test/Bruit-de-fond'
        self.stations_dict = {'SUT': ['Station-falaise', '570009'], 'REF': ['Station-reference', '570014']}
        self.timestamps = ['2016.11.06-23.59.59']
        self.test_title = 'SUT' + ' ' + self.timestamps[0]
        self.test_stream = self.get_test_stream()

    def get_test_stream(self):
        """adding traces in stream"""
        st = Stream()
        st += read(self.file1)
        st += read(self.file2)
        return st

    def test_stream(self):
        self.assertIsInstance(self.test_stream, Stream)

    def test_create_three_d_stream(self):
        """testing create_three_d_stream function"""
        st = model.create_three_d_stream(self.file1, self.file2)
        self.assertIsInstance(st, Stream)

    def test_file_truple(self):
        truple = model.file_truple(self.file_path)
        self.assertEqual(len(truple), len((1, 2, 3)))

    def test_create_three_d_stream_with_files(self):
        files = model.file_truple(self.file_path)
        st = model.create_three_d_stream(*files)
        self.assertIsInstance(st, Stream)

    def test_create_streams_dict(self):
        """
        :return: test if streams_dict actually contains streams
        """
        streams = model.create_streams_dict(self.mother_repository, self.stations_dict, self.timestamps)
        self.assertIsInstance(streams[self.test_title], Stream)

    def test_compute_decimated_spectrum(self):
        """
        Test compute_decimated_spectrum function.
        Check frequencies.
        Check if the PSD corresponding to the first frequency is not enormous (related to 'detrend' parameter)
        """
        trace = self.test_stream.traces[0]
        trace2 = trace.copy()
        decimal_value = 5
        pxx, frequencies = model.compute_decimated_spectrum(trace2, decimal_value)
        # Caution: trace2 have been overwritten
        expected_frequencies = np.linspace(0, 100/decimal_value, int(len(trace2)/2+1))
        # Testing frequencies
        np.testing.assert_equal(frequencies, expected_frequencies)
        # Testing PSD of first frequency (related to 'detrend' parameter)
        self.assertGreater(100, frequencies[0])

    def test_compute_ratio1(self):
        """
        :return: ratio of a trace over itself. Should return a np.array of 1.
        """
        data = self.test_stream.traces[0].data
        ratio = model.compute_ratio(data, data, 0)
        np.testing.assert_almost_equal(ratio, np.ones(len(data)))

    def test_compute_ratio2(self):
        num = np.arange(6).reshape(2, 3)
        den = np.arange(5, -1, -1).reshape(2, 3)
        data = np.array([0, 1/4.025, 2/3.025, 3/2.025, 4/1.025, 5/0.025]).reshape(2, 3)
        ratio = model.compute_ratio(num, den, 0.01)
        np.testing.assert_almost_equal(data, ratio)


class ControllerTest(unittest.TestCase):

        def setUp(self):
            self.mother_repository = 'data_test/Bruit-de-fond'
            self.stations_dict = {'SUT': ['Station-falaise', '570009'], 'REF': ['Station-reference', '570014']}
            self.timestamps = ['2016.11.06-23.59.59', '2016.11.06-23.59.59']
            self.streams = model.create_streams_dict(self.mother_repository, self.stations_dict, self.timestamps)

        def test_load_data(self):
            test_title = 'SUT' + ' ' + self.timestamps[0]
            self.assertIsInstance(self.streams[test_title], Stream)

        # def test_compute_spectrogram(self):
        # self.array_hour_spectro, self.spectre, self.rapport = model.compute_spectrogram(0,
        #                                                                         self.streams,
        #                                                                         self.timestamps)


class PerDeltaTest(unittest.TestCase):
    def setUp(self):
        self.start = datetime(year=2016,
                              month=11,
                              day=6,
                              hour=23,
                              minute=59,
                              second=59)
        self.end = datetime(year=2016,
                            month=11,
                            day=13,
                            hour=22,
                            minute=59,
                            second=59)
        self.time_list = model.perdelta(self.start, self.end, timedelta(hours=1))

    def test_perdelta(self):
        self.assertEqual(self.time_list[0], '2016.11.06-23.59.59')
        self.assertEqual(self.time_list[-1], '2016.11.13-22.59.59')

# ----------------------------------------------------
# switching to pytest
# using pytest-cov


@pytest.fixture()
def mother_repository():
    return 'data_test/Bruit-de-fond'


@pytest.fixture()
def station_dict():
    return {'SUT': ['Station-falaise', '570009'],
            'REF': ['Station-reference', '570014']}


@pytest.fixture()
def timestamp():
    return '2016.11.06-23.59.59'


def test_create_path():
    assert model.create_path(mother_repository,
                             station_dict,
                             'SUT',
                             timestamp,
                             'Z') \
           == "/data_test/Bruit-de-fond" \
           "Station-falaise/2016.11.06-23.59.59.AG.570009.00.C00.SAC"
