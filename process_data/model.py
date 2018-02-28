# -*- coding: utf-8 -*-
import numpy as np
from matplotlib.mlab import psd
from obspy import read


# -----------------------------------------------------------------------------------
# spectrogram functions

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
        del decimated_rt
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
        # TODO: improve RAM utilisation of this
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
        del trace
        return freqs


def compute_ratio(numerator, denominator, water_level_ratio):
    """
    :param numerator: stream, above
    :param denominator: stream, below
    :param water_level_ratio: float, % of water level, between 0 and 1
    :return: np.array: numerator over denominator modified with water level
    """

    den2 = denominator + water_level_ratio*np.mean(denominator)
    return numerator/den2

