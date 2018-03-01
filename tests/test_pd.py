# -*- coding: utf-8 -*-
import numpy as np
import process_data.model as pd_model
from obspy import read
import pytest
# https://matplotlib.org/faq/howto_faq.html#matplotlib-in-a-web-application-server
import matplotlib
matplotlib.use('Agg')
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.ticker as ticker
import os


@pytest.fixture()
def decimate_factor():
    return 15  # in order to run tests faster. Need to be smaller than 16


@pytest.fixture()
def reference_file_path():
    return 'tests/data_test/Falaise_nov2016/2016.11.06-23.59.59.AG.570009.00.C00.SAC'


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


@pytest.fixture()
def trace_processor(reference_file_path, decimate_factor):
    return pd_model.TraceProcessor(reference_file_path,
                                   decimate_factor,
                                   0.5,
                                   15)


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


def test_trace_processor_shapes(trace_processor, short_trace):
    x = [short_trace.stats.starttime]
    y = trace_processor.filtred_and_decimated_ref_freqs

    trace = short_trace.copy()
    trace_processor.filter_trace(trace)
    pxx = trace_processor.compute_decimated_spectrum(trace)[0]

    sp = np.transpose(np.array([pxx]))

    assert(sp.shape[:2] == (len(y), len(x)))


def test_plot_log_scale(trace_processor, short_trace, long_trace):

    x0 = [short_trace.stats.starttime, long_trace.stats.starttime]
    x = np.arange(len(x0))
    y = trace_processor.filtred_and_decimated_ref_freqs

    trace = short_trace.copy()
    trace_processor.filter_trace(trace)
    pxx1 = trace_processor.compute_decimated_spectrum(trace)[0]

    trace = long_trace.copy()
    trace_processor.filter_trace(trace)
    pxx2 = trace_processor.compute_decimated_spectrum(trace)[0]

    Z = np.transpose(np.array([pxx1, pxx2]))

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    picture = ax.pcolorfast(x, y, Z,
                            cmap='jet',
                            norm=colors.LogNorm(vmin=1e3, vmax=1e6),
                            )
    ax.set_yscale('log')
    plt.ylim(ymin=1, ymax=np.max(y))
    plt.colorbar(picture)

    # TODO: make this more beautiful
    img_reference = mpimg.imread('tests/figure_log_test.png')
    path = 'tests/test_log_scale.png'
    plt.savefig(path, format='png')
    img_test = mpimg.imread(path)
    os.remove(path)

    np.testing.assert_array_equal(img_test, img_reference)


def test_plot_linear_scale(trace_processor, short_trace, long_trace):

    y = np.array(trace_processor.filtred_and_decimated_ref_freqs)

    trace = short_trace.copy()
    trace_processor.filter_trace(trace)
    pxx1 = trace_processor.compute_decimated_spectrum(trace)[0]

    trace = long_trace.copy()
    trace_processor.filter_trace(trace)
    pxx2 = trace_processor.compute_decimated_spectrum(trace)[0]

    Z = np.transpose(np.array([pxx1, pxx2]))

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    picture = ax.pcolorfast(np.arange(2), y, Z,
                            cmap='jet',
                            norm=colors.LogNorm(vmin=1e3, vmax=1e6),
                            )
    #ax.xaxis_date()
    #plt.xlim(xmin=x[0], xmax=x[-1])
    # ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    # ax.xaxis.set_major_locator(mdates.DayLocator)
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # ax.autoscale_view()

    #ax.set_yscale('log')
    plt.ylim(ymin=1, ymax=np.max(y))

    plt.colorbar(picture)

    # TODO: make this more beautiful
    img_reference = mpimg.imread('tests/figure_linear_test.png')
    path = 'tests/test_linear_scale.png'
    plt.savefig(path, format='png')
    img_test = mpimg.imread(path)
    os.remove(path)

    np.testing.assert_array_equal(img_test, img_reference)


def test_plot_x_axis_as_date(trace_processor, short_trace, long_trace):
    x_ticks_labels = [short_trace.stats.starttime,
                      long_trace.stats.starttime,
                      long_trace.stats.starttime] + [long_trace.stats.endtime]

    x = np.arange(len(x_ticks_labels))

    y = trace_processor.filtred_and_decimated_ref_freqs

    trace = short_trace.copy()
    trace_processor.filter_trace(trace)
    pxx1 = trace_processor.compute_decimated_spectrum(trace)[0]

    trace = long_trace.copy()
    trace_processor.filter_trace(trace)
    pxx2 = trace_processor.compute_decimated_spectrum(trace)[0]

    trace = long_trace.copy()
    trace_processor.filter_trace(trace)
    pxx3 = trace_processor.compute_decimated_spectrum(trace)[0]

    Z = np.transpose(np.array([pxx1, pxx2, pxx3]))

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    picture = ax.pcolorfast(x, y, Z,
                            cmap='jet',
                            norm=colors.LogNorm(vmin=1e3, vmax=1e6),
                            )

    # managing x axe: replace xticklabels by hand
    # after https://stackoverflow.com/questions/17129947/how-to-set-ticks-on-fixed-position-matplotlib
    name_list = [elt.date.isoformat() for elt in x_ticks_labels]
    ax.xaxis.set_major_locator(ticker.FixedLocator(x))
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(name_list))

    # managing y axe
    ax.set_yscale('log')
    plt.ylim(ymin=1, ymax=np.max(y))

    plt.colorbar(picture)

    # TODO: make this more beautiful
    img_reference = mpimg.imread('tests/figure_x_axis_as_date_test.png')
    path = 'tests/figure_x_axis_as_date_tested.png'
    plt.savefig(path, format='png')
    img_test = mpimg.imread(path)
    os.remove(path)

    np.testing.assert_array_equal(img_test, img_reference)