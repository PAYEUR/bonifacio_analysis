# -*- coding: utf-8 -*-
import numpy as np
from matplotlib.mlab import psd


# -----------------------------------------------------------------------------------
# spectrogram functions
def compute_decimated_spectrum(trace, reference_trace, decimal_value):
    """
    :param trace:
    :param reference_trace: trace corresponding to the maximal size file
    :param decimal_value: int, beetween 1 and +infinity

    :return: decimate trace and return frequencies and spectrum arrays
    """

    decimated_t = trace.copy().decimate(decimal_value)
    decimated_rt = reference_trace.copy().decimate(decimal_value)
    p_xx, frequencies = psd(decimated_t,
                            #NFFT=max_trace_length,
                            NFFT=len(decimated_t)//4,
                            pad_to=len(decimated_rt),
                            Fs=decimated_t.stats.sampling_rate,
                            detrend='mean',
                            #noverlap=1000,
                            )
    return p_xx, frequencies


def compute_ratio(numerator, denominator, water_level_ratio):
    """
    :param numerator: stream, above
    :param denominator: stream, below
    :param water_level_ratio: float, % of water level, between 0 and 1
    :return: np.array: numerator over denominator modified with water level
    """

    den2 = denominator + water_level_ratio*np.mean(denominator)
    return numerator/den2

