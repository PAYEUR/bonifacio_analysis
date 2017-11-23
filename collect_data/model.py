# -*- coding: utf-8 -*-
import numpy as np
from obspy import read
from obspy.core.stream import Stream
from matplotlib.mlab import psd


# Time functions
def perdelta(start, end, delta):
    """
    :param start: datetime.datetime
    :param end: datetime.datetime
    :param delta: datetime.timedelta
    :return: list of string in strf "%Y.%m.%d-%H.%M.%S" format
    """
    strf = "%Y.%m.%d-%H.%M.%S"
    time_list = [start.strftime(strf)]
    curr = start
    while curr < end:
        curr += delta
        time_list.append(curr.strftime(strf))
    return time_list


# -----------------------------------------------------------------------------------
# controller 1 files and stream manager functions
def create_three_d_stream(*files):
    """
    :param files: one or many strings. Each string is the name of file path
    :return: obspy.Stream. Each file is a stream.trace
    """
    st = Stream()
    for file in files:
        st += read(file)
    return st


def create_streams_dict(mother_repository, stations_dict, timestamps):
    """
    :param mother_repository: string, path of mother repository
    :param stations_dict: dict, stations parameters
    :param timestamps: list of timestamps given as strings
    :return a dict of streams:
        :key : string, name of station and timestamp
        :value : obspy.Stream for the given hour and station.
                 st.trace[0]: Z, st.trace[1]: N and st.trace[2]: E
    """
    streams = dict()
    for k, v in stations_dict.items():
        repository = mother_repository + '/' + v[0]
        for timestamp in timestamps:
            files = file_truple(repository + '/' + timestamp + '.AG.' + v[1] + '.00.')
            st = create_three_d_stream(*files)
            title = k + ' ' + timestamp
            streams[title] = st
    return streams


def file_truple(file_path):
    """
    :param file_path: string, path of the repository
    :return: tuple of 3 stings: name of Z, N and E data files
    """
    file1 = file_path + "C00" + ".SAC"
    file2 = file_path + "C01" + ".SAC"
    file3 = file_path + "C02" + ".SAC"
    return file1, file2, file3


# -----------------------------------------------------------------------------------
# controller 1 files and stream manager functions
def create_path(mother_repository, stations_dict, station, timestamp, direction):
    """

    :param mother_repository: string, path of mother repository
    :param stations_dict: dict, stations parameters
    :param station: 'SUT' or 'REF', key of station_dict
    :param timestamp: string, timestamp
    :param direction: 'Z', 'N' or 'E'
    :return:
        string, path of corresponding file
    """
    if direction == 'Z':
        index = "00"
    elif direction == 'N':
        index = '01'
    elif direction == 'E':
        index = '02'

    return f"{mother_repository}/{stations_dict[station][0]}/" \
           f"{timestamp}.AG.{stations_dict[station][1]}.00." \
           f"C{index}.SAC"


# -----------------------------------------------------------------------------------
# spectrogram functions
def compute_decimated_spectrum(trace, decimal_value):
    """
    :param trace:
    :param decimal_value: int, beetween 1 and +infinity
    :return: decimate trace and return frequencies and spectrum arrays
    """
    trace.decimate(decimal_value)
    p_xx, frequencies = psd(trace,
                            NFFT=len(trace)//4,
                            pad_to=len(trace),
                            Fs=trace.stats.sampling_rate,
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


# controller function
# TODO: this should become depreciated as controller will be rewritten
def compute_spectrogram(station_name_with_blank, direction_index, streams, timestamps):

    hours_spectros = []
    for timestamp in timestamps:
        key = station_name_with_blank + timestamp
        p_xx, freqs = compute_decimated_spectrum(streams[key].traces[direction_index], decimal_value=5)
        hours_spectros.append(p_xx)
    return np.array(hours_spectros), freqs
