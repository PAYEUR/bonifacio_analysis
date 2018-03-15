# -*- coding: utf-8 -*-
import pytest
import numpy as np
from obspy import read

import process_data.model as pd_model
from root import root


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


def test_get_pad_to_value(trace_processor, reference_file_path, decimate_factor):
    reference_trace = read(reference_file_path)[0]
    reference_trace_decimated = reference_trace.copy().decimate(decimate_factor)
    expected_length = len(reference_trace_decimated)

    assert expected_length == trace_processor.pad_to


def test_compute_decimated_spectrum_same_file_size(trace_processor, long_trace):
    """
    Test compute_decimated_spectrum function.
    Check frequencies.
    Check if the PSD corresponding to the first frequency is not enormous (related to 'detrend' parameter)
    """

    pxx, frequencies = trace_processor.compute_decimated_spectrum(long_trace.copy())

    # build reference data
    decimated_t = long_trace.copy().decimate(trace_processor.decimate_factor)
    decimated_rt = trace_processor.reference_trace.copy().decimate(trace_processor.decimate_factor)
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


def test_compute_decimated_spectrum_different_file_size(trace_processor, long_trace, short_trace):

    psd1 = trace_processor.compute_decimated_spectrum(long_trace.copy())
    psd2 = trace_processor.compute_decimated_spectrum(short_trace.copy())

    assert np.shape(psd1) == np.shape(psd2)


def test_compute_decimated_spectrum_merged_trace(trace_processor, merged_trace_fill_value_0):

    psd1 = trace_processor.compute_decimated_spectrum(trace_processor.reference_trace.copy())
    psd2 = trace_processor.compute_decimated_spectrum(merged_trace_fill_value_0.copy())

    assert np.shape(psd1) == np.shape(psd2)


def test_compute_decimated_spectrum_merged_trace_fail(trace_processor, merged_trace_fill_value_none):

    with pytest.raises(NotImplementedError):
        trace_processor.compute_decimated_spectrum(merged_trace_fill_value_none.copy())


def test_filter_trace(trace_processor):

    filter_test = trace_processor.filter_trace(trace_processor.reference_trace.copy())

    reference_test = trace_processor.reference_trace.copy().filter('bandpass',
                                                                   freqmin=0.5,
                                                                   freqmax=15,
                                                                   )

    assert filter_test == reference_test


def test_trace_processor_shapes(short_psd, short_trace):
    # test if frequencies, datetime_list and psd get the expected shape
    x = [short_trace.stats.starttime]
    freqs, sp = short_psd

    # np.savetxt('freq.test', y, fmt='%1.10e')
    # np.savetxt('sp.test', sp, fmt='%1.4e')

    assert(sp.shape[:2] == (len(freqs), len(x)))


def test_get_array(short_psd):
    _, ref_sp = short_psd
    test_sp = pd_model.get_array(str(root / 'tests/data_test/sp.test'))

    assert np.allclose(ref_sp, test_sp, rtol=1e-4)


def test_get_frequencies(short_psd):
    ref_freqs, _ = short_psd
    test_freqs = pd_model.get_frequencies(str(root/'tests/data_test/freq.test'))

    assert np.allclose(ref_freqs, test_freqs, rtol=1e-10)


def test_compute_ratio_fast():
    num = np.array([[1, 2], [3, 4], [0, 6]])
    ratio = pd_model.compute_ratio(num, num, 0.1)
    assert np.max(ratio) + 0.2 > 1 # 20% of difference
    assert np.max(ratio) < 1


def test_compute_ratio_real_data(short_psd):
    _, ref_sp = short_psd
    ratio = pd_model.compute_ratio(ref_sp, ref_sp, 0.05)
    assert np.max(ratio) + 0.2 > 1  # 20% of difference
    assert np.max(ratio) < 1


def test_remove_noisy_columns_fast():
    a = np.array([[0, 0, 1], [0, 0, 1]])
    b = np.zeros(a.shape)
    a_filtered = pd_model.remove_noisy_columns(a, 1)
    assert np.array_equal(a_filtered, b)
