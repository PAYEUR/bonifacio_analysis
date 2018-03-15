# -*- coding: utf-8 -*-
from datetime import timedelta

import numpy as np
import pandas
from matplotlib.mlab import psd
from obspy import read
from scipy.ndimage import gaussian_filter


# -----------------------------------------------------------------------------------
# spectrogram functions

def get_array(sp_file_path):
    return pandas.read_csv(str(sp_file_path), sep=' ', header=None, dtype=np.float64).values


class TraceProcessor:

    def __init__(self,
                 reference_file_path,
                 decimate_factor,
                 freqmin,
                 freqmax,
                 ):
        self.reference_file_path = reference_file_path
        self.decimate_factor = decimate_factor
        self.freqmin = freqmin
        self.freqmax = freqmax
        self.reference_trace = read(self.reference_file_path)[0]
        self.pad_to = self.get_pad_to_value()
        self.filtred_and_decimated_ref_freqs = self.get_filtred_and_decimated_ref_freqs()

    def get_pad_to_value(self):
        decimated_rt = self.reference_trace.copy().decimate(self.decimate_factor)
        pad_to_value = len(decimated_rt)
        return pad_to_value

    def filter_trace(self, trace):
        """
        :param trace: obspy.trace
        :return:
        """
        # https://docs.obspy.org/tutorial/code_snippets/filtering_seismograms.html
        # https://docs.obspy.org/packages/autogen/obspy.signal.filter.bandpass.html#obspy.signal.filter.bandpass

        return trace.filter('bandpass',
                            freqmin=self.freqmin,
                            freqmax=self.freqmax,
                            )

    def compute_decimated_spectrum(self, trace):
        """
        :param trace: obspy.trace that is decimated
        :return: decimate trace and return frequencies and spectrum arrays
        """
        trace.decimate(self.decimate_factor)

        p_xx, frequencies = psd(trace,
                                #NFFT=max_trace_length,
                                NFFT=len(trace)//4,
                                pad_to=self.pad_to,
                                Fs=trace.stats.sampling_rate,
                                detrend='mean',
                                #noverlap=1000,
                                )
        return p_xx, frequencies

    def get_filtred_and_decimated_ref_freqs(self):
        trace = self.reference_trace.copy()
        freqs = self.compute_decimated_spectrum(self.filter_trace(trace))[1]
        return freqs


class RatioManager:

    def __init__(self,
                 sp_cliff_file_path,
                 sp_reference_file_path,
                 frequencies_file_path,
                 start_time,
                 end_time,
                 ):

        self.sp_cliff_file_path = sp_cliff_file_path
        self.sp_reference_file_path = sp_reference_file_path
        self.frequencies_file_path = frequencies_file_path
        self.start_time = start_time
        self.end_time = end_time
        self.frequencies = self.get_frequencies()
        self.datetime_list = self.get_datetime_list()
        self.ratio = self.compute_ratio(0.05)

    def get_frequencies(self):
        return pandas.read_csv(str(self.frequencies_file_path),
                               sep=' ',
                               header=None,
                               dtype=np.float64).values.flatten()

    def get_datetime_list(self):

        datetime_list = []
        t = self.start_time
        while t < self.end_time:
            datetime_list.append(t)
            t += timedelta(hours=1)
        return datetime_list

    def compute_ratio(self, water_level_ratio):
        """
        :param water_level_ratio: float, % of water level, between 0 and 1
        :return: np.array: numerator over denominator modified with water level
        """
        numerator = get_array(self.sp_cliff_file_path)
        denominator = get_array(self.sp_reference_file_path)
        den2 = denominator + water_level_ratio*np.mean(denominator)
        return numerator/den2

    def remove_noisy_columns(self, noise_level):
        """
        remove hours that are too noisy (assume first column ok) and replace with previous column
        :param noise_level float, noise threshold above mean noise
        :return: np.array, ratio
        """
        i = 1
        ratio = self.ratio
        while i < ratio.shape[1]:
            if np.mean(ratio[:, i]) > noise_level * np.mean(ratio):
                ratio[:, i] = ratio[:, i - 1]
            i += 1

    def smooth(self, sigma):
        """
        :param sigma: tuple of float. Interpolation between adjacent array cells in y and x
        :return: np.array, ratio
        """
        self.ratio = gaussian_filter(self.ratio, sigma=sigma)

