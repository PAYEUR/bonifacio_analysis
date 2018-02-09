# -*- coding: utf-8 -*-
import numpy as np
import obspy
from datetime import datetime, timedelta
from obspy.core.stream import Stream
from matplotlib.mlab import psd
import re


class TraceManager:

    def __init__(self, repository_path):
        self.repository_path = repository_path
        self.sorted_traces = self.sort_traces

    def sort_traces(self):
        """
        :return: Read all SAC files of the folder and return an array sorted-by-starttime traces
        """
        unsorted_traces = []
        for file_path in list(self.repository_path.glob('*.SAC')):
            stream = obspy.read(file_path)
            trace = stream[0]  # in the bonifacio configuration
            unsorted_traces.append(trace)

        # sorting it
        sorted_traces = sorted(unsorted_traces, key=lambda trace: trace.stats.starttime)

        self.merge_same_hour(sorted_traces)

        return sorted_traces

    def merge_same_hour(self, first_sorted_traces):
        repository_start_time = first_sorted_traces[0].stats.starttime
        repository_end_time = first_sorted_traces[-1].stats.endtime
        current_time = repository_start_time
        while current_time < repository_end_time:
            st = obspy.Stream()
            i = 0
            # count number of traces within the same hour
            for trace in first_sorted_traces:
                if trace.t.stats.starttime.hour == current_time.hour:
                    st.traces[i] = trace
                    i += 1
            # merge them
            st.merge(method=1)

            current_time = current_time + timedelta(hours=1)


            # Time functions
def perdelta(start, end, delta):
    """
    :param start: datetime.datetime
    :param end: datetime.datetime
    :param delta: datetime.timedelta
    :return: list of string in strf "%Y.%m.%d-%H.%M.%S" format
    """
    strf = "%Y.%m.%d-%H"
    time_list = [start.strftime(strf)]
    curr = start
    while curr < end:
        curr += delta
        time_list.append(curr.strftime(strf))
    return time_list


# -----------------------------------------------------------------------------------
# files and stream manager functions
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
        index = '00'
    elif direction == 'N':
        index = '01'
    elif direction == 'E':
        index = '02'

    return f"{mother_repository}/{stations_dict[station][0]}/" \
           f"{timestamp}.*.AG.{stations_dict[station][1]}.00." \
           f"C{index}.SAC"

