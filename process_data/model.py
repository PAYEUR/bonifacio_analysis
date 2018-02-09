# -*- coding: utf-8 -*-
import numpy as np
from obspy import read
from obspy.core.stream import Stream
from matplotlib.mlab import psd
from collect_data import model
import re


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


# -----------------------------------------------------------------------------------
# controller function

def compute_spectrogram(timestamps,
                        mother_repository,
                        stations_dict,
                        station,
                        direction,
                        decimal_value,
                        reference_trace):
    """
    :param timestamps:
    :param mother_repository:
    :param stations_dict:
    :param station:
    :param direction:
    :param decimal_value
    :param reference_trace
    :return:
    """
    hours_spectros = []
    freqs = None

    for timestamp in timestamps:
        path = model.create_path(mother_repository, stations_dict, station, timestamp, direction)
        trace = read(path)[0]
        if freqs is None:
            p_xx, freqs = compute_decimated_spectrum(trace, reference_trace, decimal_value)
        else:
            p_xx = compute_decimated_spectrum(trace, reference_trace, decimal_value)[0]
        hours_spectros.append(p_xx)

    sp = np.transpose(np.array(hours_spectros))
    return sp, freqs
