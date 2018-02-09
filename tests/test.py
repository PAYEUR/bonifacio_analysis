# -*- coding: utf-8 -*-
import unittest
import numpy as np
import collect_data.model as cd_model
import process_data.model as pd_model
from obspy import read
from datetime import datetime, timedelta
import pytest
from numpy.testing import assert_array_equal
# import re


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
        self.time_list = cd_model.perdelta(self.start, self.end, timedelta(hours=1))

    def test_perdelta(self):
        self.assertEqual(self.time_list[0], '2016.11.06-23')
        self.assertEqual(self.time_list[-1], '2016.11.13-22')


# ----------------------------------------------------
# switching to pytest
# using pytest-cov


@pytest.fixture()
def mother_repository():
    return 'tests/data_test'


@pytest.fixture()
def station_dict():
    return {'SUT': ['Station-falaise', '570009'],
            'REF': ['Station-reference', '570014'],
            }


@pytest.fixture()
def timestamps():
    return ['2016.11.06-23', '2016.11.09-17']


@pytest.fixture()
def decimal_value():
    return 15  # in order to run tests faster. Need to be smaller than 16


@pytest.fixture()
def path_reference_file():
    return "tests/data_test/Station-falaise/2016.11.06-23.59.59.AG.570009.00.C00.SAC"


@pytest.fixture()
def reference_trace(path_reference_file):
    return read(path_reference_file)[0]


@pytest.fixture()
def path_short_file():
    return "tests/data_test/Station-reference/2016.11.09-17.59.59.AG.570014.00.C00.SAC"


@pytest.fixture()
def path_long_file():
    return "tests/data_test/Station-falaise/2016.11.09-17.59.59.AG.570009.00.C00.SAC"


def test_create_path(mother_repository, station_dict, timestamps, path_reference_file):

    built_path = cd_model.create_path(mother_repository,
                                      station_dict,
                                      'SUT',
                                      timestamps[0],
                                      'Z')
    st1 = read(built_path)
    st2 = read(path_reference_file)

    assert st1 == st2


def test_compute_decimated_spectrum_same_file_size(reference_trace, decimal_value):
    """
    Test compute_decimated_spectrum function.
    Check frequencies.
    Check if the PSD corresponding to the first frequency is not enormous (related to 'detrend' parameter)
    """

    pxx, frequencies = pd_model.compute_decimated_spectrum(trace=reference_trace,
                                                           reference_trace=reference_trace,
                                                           decimal_value=decimal_value)

    # build reference data
    decimated_t = reference_trace.copy().decimate(decimal_value)
    decimated_rt = reference_trace.copy().decimate(decimal_value)
    fs = decimated_t.stats.sampling_rate
    # not totally equal because of decimate function
    # => can check shape only
    expected_frequencies = np.linspace(0,
                                       (fs+1) / 2,
                                       int(len(decimated_rt) / 2 + 1))

    # Testing frequencies
    assert np.shape(frequencies) == np.shape(expected_frequencies)
    # Testing PSD of first frequency (related to 'detrend' parameter)
    assert 100 > frequencies[0]


def test_compute_decimated_spectrum_different_file_size(decimal_value,
                                                        path_short_file,
                                                        path_long_file,
                                                        reference_trace):

    long_trace = read(path_long_file)[0]
    short_trace = read(path_short_file)[0]

    p_xx_1 = pd_model.compute_decimated_spectrum(long_trace, reference_trace, decimal_value)
    p_xx_2 = pd_model.compute_decimated_spectrum(short_trace, reference_trace, decimal_value)

    assert np.shape(p_xx_1) == np.shape(p_xx_2)


def test_compute_spectrogram(path_short_file,
                             timestamps,
                             mother_repository,
                             station_dict,
                             reference_trace,
                             decimal_value):

    # test compute_spectrogram function for station REF
    test_sp, test_freqs = pd_model.compute_spectrogram(timestamps,
                                                       mother_repository,
                                                       station_dict,
                                                       'REF',
                                                       'Z',
                                                       decimal_value,
                                                       reference_trace)


    # building data to test
    path0 = "tests/data_test/Station-reference/2016.11.06-23.59.59.AG.570014.00.C00.SAC"
    path1 = "tests/data_test/Station-reference/2016.11.09-17.59.59.AG.570014.00.C00.SAC"
    p_xx_0, freqs = pd_model.compute_decimated_spectrum(read(path0)[0], reference_trace, decimal_value)
    p_xx_1 = pd_model.compute_decimated_spectrum(read(path1)[0], reference_trace, decimal_value)[0]

    # testing spectrogram functions with data.
    # as it handle with np.arrays one have to use np.testing.assert_array_equal

    assert_array_equal(test_sp, np.transpose(np.array([p_xx_0, p_xx_1])))
    assert_array_equal(freqs, test_freqs)



