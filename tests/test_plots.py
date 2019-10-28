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


def assert_same_image_as(path_reference):
    """ Compare image that is currently built with image from path reference
        and raise and AssertionError if they are not identical
    """
    path_tested = 'tests/figure_test/test.png'
    img_reference = mpimg.imread(path_reference)
    plt.savefig(path_tested, format='png')
    img_test = mpimg.imread(path_tested)
    os.remove(path_tested)
    np.testing.assert_allclose(img_test, img_reference, rtol=1.02, atol=1.0)


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
