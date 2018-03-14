# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta

import numpy as np
# https://matplotlib.org/faq/howto_faq.html#matplotlib-in-a-web-application-server
import matplotlib
matplotlib.use('Agg')
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.ticker as ticker


def assert_same_image_as(path_reference):
    """ Compare image that is currently built with image from path reference
        and raise and AssertionError if they are not identical
    """
    path_tested = 'tests/figure_test/test.png'
    img_reference = mpimg.imread(path_reference)
    plt.savefig(path_tested, format='png')
    img_test = mpimg.imread(path_tested)
    os.remove(path_tested)
    np.testing.assert_array_equal(img_test, img_reference)


def test_log_scale(trace_processor, short_trace, long_trace):

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

    assert_same_image_as(path_reference='tests/figure_test/figure_log_test.png')


def test_linear_scale(trace_processor, short_trace, long_trace):

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

    plt.ylim(ymin=1, ymax=np.max(y))

    plt.colorbar(picture)

    assert_same_image_as(path_reference='tests/figure_test/figure_linear_test.png')


def test_x_axis_as_date(trace_processor, short_trace, long_trace):

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

    trace = short_trace.copy()
    trace_processor.filter_trace(trace)
    pxx4 = trace_processor.compute_decimated_spectrum(trace)[0]

    trace = long_trace.copy()
    trace_processor.filter_trace(trace)
    pxx5 = trace_processor.compute_decimated_spectrum(trace)[0]

    trace = long_trace.copy()
    trace_processor.filter_trace(trace)
    pxx6 = trace_processor.compute_decimated_spectrum(trace)[0]

    pxx_array = [pxx1, pxx2, pxx3, pxx4, pxx5, pxx6]

    # for example purpose only
    today = datetime.today()
    x_ticks_labels = []
    for i, _ in enumerate(pxx_array):
        x_ticks_labels.append(today + timedelta(days=i))

    # Don't forget to add the last end_time at the end of x_ticks_labels!!
    x_ticks_labels.append(today + timedelta(days=len(pxx_array)))

    x = np.arange(len(x_ticks_labels))
    Z = np.transpose(np.array(pxx_array))

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    picture = ax.pcolorfast(x, y, Z,
                            cmap='jet',
                            norm=colors.LogNorm(vmin=1e3, vmax=1e6),
                            )

    # after https://stackoverflow.com/questions/17129947/how-to-set-ticks-on-fixed-position-matplotlib
    name_list = [elt.strftime('%a %d %b') for elt in x_ticks_labels]
    x_labels_interval = 3
    ax.xaxis.set_major_locator(ticker.FixedLocator(x[::x_labels_interval]))
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(name_list[::x_labels_interval]))
    plt.xticks(rotation=70)

    # managing y axe
    ax.set_yscale('log')
    plt.ylim(ymin=1, ymax=np.max(y))

    plt.colorbar(picture)

    # plt.savefig('tests/figure_test/figure_x_axis_as_date_test.png', format='png')

    assert_same_image_as(path_reference='tests/figure_test/figure_x_axis_as_date_test.png')
