# -*- coding: utf-8 -*-
import numpy as np
import process_data.model as pd_model
from obspy import read
import pytest


@pytest.fixture()
def decimal_value():
    return 15  # in order to run tests faster. Need to be smaller than 16


@pytest.fixture()
def reference_trace():
    return read('tests/data_test/Falaise_nov2016/2016.11.06-23.59.59.AG.570009.00.C00.SAC')[0]


@pytest.fixture()
def short_trace():
    return read('tests/data_test/Ref_nov2016/2016.11.09-17.59.59.AG.570014.00.C00.SAC')[0]


@pytest.fixture()
def long_trace():
    return read('tests/data_test/Falaise_nov2016/2016.11.09-17.59.59.AG.570009.00.C00.SAC')[0]


@pytest.fixture()
def merged_trace_fill_value_0():
    trace1 = read('tests/data_test/Falaise_Janv2017/2017.01.13-02.16.51.AG.570009.00.C00.SAC')[0]
    trace2 = read('tests/data_test/Falaise_Janv2017/2017.01.13-02.57.33.AG.570009.00.C00.SAC')[0]
    # https://docs.obspy.org/packages/autogen/obspy.core.trace.Trace.__add__.html#obspy.core.trace.Trace.__add__
    return trace1.__add__(trace2, fill_value=0)


@pytest.fixture()
def merged_trace_fill_value_none():
    trace1 = read('tests/data_test/Falaise_Janv2017/2017.01.13-02.16.51.AG.570009.00.C00.SAC')[0]
    trace2 = read('tests/data_test/Falaise_Janv2017/2017.01.13-02.57.33.AG.570009.00.C00.SAC')[0]
    # https://docs.obspy.org/packages/autogen/obspy.core.trace.Trace.__add__.html#obspy.core.trace.Trace.__add__
    return trace1.__add__(trace2)


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
                                                        short_trace,
                                                        long_trace,
                                                        reference_trace):

    p_xx_1 = pd_model.compute_decimated_spectrum(long_trace, reference_trace, decimal_value)
    p_xx_2 = pd_model.compute_decimated_spectrum(short_trace, reference_trace, decimal_value)

    assert np.shape(p_xx_1) == np.shape(p_xx_2)


def test_compute_decimated_spectrum_merged_trace(reference_trace,
                                                 merged_trace_fill_value_0,
                                                 decimal_value):

    p_xx_1 = pd_model.compute_decimated_spectrum(reference_trace,
                                                 reference_trace,
                                                 decimal_value)
    p_xx_2 = pd_model.compute_decimated_spectrum(merged_trace_fill_value_0,
                                                 reference_trace,
                                                 decimal_value)

    assert np.shape(p_xx_1) == np.shape(p_xx_2)


def test_compute_decimated_spectrum_merged_trace_fail(reference_trace,
                                                      merged_trace_fill_value_none,
                                                      decimal_value):

    result = False
    try:
        pd_model.compute_decimated_spectrum(merged_trace_fill_value_none,
                                            reference_trace,
                                            decimal_value)
    except NotImplementedError:
        result = True

    assert result is True
