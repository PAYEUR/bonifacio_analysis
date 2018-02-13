# -*- coding: utf-8 -*-
import obspy
import glob
from datetime import timedelta


class TraceManager:

    def __init__(self,
                 repository_path,
                 file_name_regexp,
                 start_at_59=True,
                 sort_by=lambda trace: trace.stats.starttime
                 ):

        self.repository_path = repository_path
        self.file_name_regexp = file_name_regexp
        self.start_at_59 = start_at_59
        self.sort_by = sort_by
        self.traces = self.merge_traces()

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
        sorted_traces = sorted(unsorted_traces, key=self.sort_by)
        return sorted_traces

    def merge_traces(self):
        """
        :return: array of obspy.traces sorted by starttime and merged if some traces are within the same hour
        """

        unmerged_traces = self.sort_traces()
        merged_traces = []
        i = 0
        stacked_traces = unmerged_traces[0]
        while i < len(unmerged_traces)-1:
            current_trace = unmerged_traces[i]
            next_trace = unmerged_traces[i+1]

            is_same_hour = self.is_same_hour(current_trace, next_trace)

            if is_same_hour:
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

    def is_same_hour(self, trace1, trace2):
        """
        Build assertions for if-loop depending on self.start_at_59, trace.starttime and trace.endtime.
        If self.start_at_59 is true, then XXh59-59 is considered to be equal to XX+1h00-00
        For example:
        09h59-59 == 10h00-00 is True
        If self.start_at_59 is false, then the condition is only on entire value of hour
        For example:
        09h59-59 is considered to be part of 09h
        10h00-00 is considered to be part of 10h
        Then 09h59-59 == 10h00-00 is False
        :param trace1: obspy.trace
        :param trace2: obspy.trace
        :return: Assertion on trace1.start_time and trace2.starttime
        """

        t1_start_time = trace1.stats.starttime
        # t1_end_time = trace1.stats.endtime
        t2_start_time = trace2.stats.starttime
        # t2_end_time = trace2.stats.endtime

        if self.start_at_59 is True:
            # add 2 seconds to get same hour from XXh 59min 59 sec
            t1_start_time += timedelta(seconds=2)
            t2_start_time += timedelta(seconds=2)

        return t1_start_time.hour == t2_start_time.hour

    def get_starttimes(self):
        """
        :return: an array of self.sorted_and_merged_traces starttimes
        """
        return [trace.stats.starttime for trace in self.traces]

    def get_endtimes(self):
        """
        :return: an array of self.sorted_and_merged_traces endtimes
        """
        return [trace.stats.endtime for trace in self.traces]


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

