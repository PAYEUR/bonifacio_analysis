# -*- coding: utf-8 -*-
import numpy as np
import obspy
import glob
from datetime import datetime, timedelta
from obspy.core.stream import Stream
from matplotlib.mlab import psd
import re


class TraceManager:

    def __init__(self, repository_path, file_name_regexp):
        self.repository_path = repository_path
        self.file_name_regexp = file_name_regexp
        self.sorted_and_merged_traces = self.sort_and_merge_traces()

    def sort_traces(self):
        """
        :return: Read all SAC files of the folder and return an array sorted-by-starttime traces
        """
        unsorted_traces = []
        files_list = glob.glob(self.repository_path + self.file_name_regexp)
        for file_path in files_list:
            stream = obspy.read(file_path)
            trace = stream[0]  # in the bonifacio configuration
            unsorted_traces.append(trace)

        # sorting it
        sorted_traces = sorted(unsorted_traces, key=lambda trace: trace.stats.starttime)
        return sorted_traces

    def merge_same_hour(self, unmerged_traces):
        """
        :param unmerged_traces: array of obspy.traces sorted by starttime
        :return: array of obspy.traces sorted by starttime and merged if some traces are within the same hour
        """

        merged_traces = []
        i = 0
        stacked_traces = unmerged_traces[0]
        while i < len(unmerged_traces)-1:
            current_trace = unmerged_traces[i]
            next_trace = unmerged_traces[i+1]
            if current_trace.stats.starttime.hour == next_trace.stats.starttime.hour:
                stacked_traces += next_trace
            else:  # if no more hour in common
                # save previous step
                merged_traces.append(stacked_traces)
                # reset stacked_traces
                stacked_traces = next_trace
            i += 1

        # add last element
        merged_traces.append(stacked_traces)

        return merged_traces

    def sort_and_merge_traces(self):
        return self.merge_same_hour(self.sort_traces())

    def get_starttimes(self):
        return [trace.stats.starttime for trace in self.sorted_and_merged_traces]

    def get_endtimes(self):
        return [trace.stats.endtime for trace in self.sorted_and_merged_traces]







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

