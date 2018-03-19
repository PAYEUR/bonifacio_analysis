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


def test_get_frequencies(short_psd, ratio_manager):
    ref_freqs, _ = short_psd
    test_freqs = ratio_manager.frequencies

    assert np.allclose(ref_freqs, test_freqs, rtol=1e-10)


def test_compute_ratio(ratio_manager):
    ratio = ratio_manager.ratio  # remember that ratio is supposed to be np.ones()
    assert np.max(ratio) + 0.2 > 1  # less than 20% of difference
    assert np.max(ratio) < 1


def test_ratio_manager_shapes(ratio_manager):
    rm = ratio_manager
    f = rm.frequencies
    x = rm.datetime_list
    assert rm.ratio.shape == (f.shape[0], len(x))


def test_remove_noisy_columns_fast(ratio_manager):
    a = np.array([[0, 0, 1], [0, 0, 1]])
    # replace ratio_manager.ratio by something easier
    ratio_manager.ratio = a
    b = np.zeros(a.shape)

    ratio_manager.remove_noisy_columns(noise_level=1)

    assert np.array_equal(ratio_manager.ratio, b)


def test_smooth_fast(ratio_manager):
    a = np.array([[0, 1, 2], [3, 4, 5]])
    b1 = np.array([[0, 1, 1], [3, 4, 4]])
    b2 = np.array([[1, 2, 3], [1, 2, 3]])

    # replace ratio_manager.ratio by something easier
    ratio_manager.ratio = a
    ratio_manager.smooth(sigma=(0, 3))
    assert np.array_equal(ratio_manager.ratio, b1)

    ratio_manager.ratio = a
    ratio_manager.smooth(sigma=(3, 0))
    assert np.array_equal(ratio_manager.ratio, b2)
