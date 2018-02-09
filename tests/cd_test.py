# -*- coding: utf-8 -*-
import collect_data.model as cd_model
from obspy import read
import pytest
from pathlib import Path
from datetime import timedelta


#
#
# @pytest.fixture()
# def station_dict():
#     return {'SUT': ['Falaise_nov2016', '570009'],
#             'REF': ['Ref_nov2016', '570014'],
#             }
#
#
# @pytest.fixture()
# def timestamps():
#     return ['2016.11.06-23', '2016.11.09-17']
#
#
# @pytest.fixture()
# def decimal_value():
#     return 15  # in order to run tests faster. Need to be smaller than 16
#
#
# @pytest.fixture()
# def path_reference_file():
#     return "tests/data_test/Falaise_nov2016/2016.11.06-23.59.59.AG.570009.00.C00.SAC"
#
#
# @pytest.fixture()
# def reference_trace(path_reference_file):
#     return read(path_reference_file)[0]
#
#



#@pytest.fixture()
#def path_long_file():
#    return "tests/data_test/Falaise_nov2016/2016.11.09-17.59.59.AG.570009.00.C00.SAC"


# def test_create_path(mother_repository_path, station_dict, timestamps, path_reference_file):
#
#     built_path = cd_model.create_path(mother_repository_path,
#                                       station_dict,
#                                       'SUT',
#                                       timestamps[0],
#                                       'Z')
#     st1 = read(built_path)
#     st2 = read(path_reference_file)
#
#     assert st1 == st2


# Trace tests
# @pytest.fixture()
# def path_short_file():
#     return "tests/data_test/Ref_nov2016/2016.11.09-17.59.59.AG.570014.00.C00.SAC"
#
# @pytest.fixture()
# def trace(path_short_file):
#     return cd_model.Trace(path_short_file)
#
#
# def test_trace(trace, path_short_file):
#     st = read(path_short_file)
#     assert trace.trace == st[0]
#
#
# def test_start_time(trace, path_short_file):
#     assert trace.start_time == read(path_short_file)[0].stats.starttime
#
#
# def test_start_time_string(trace):
#     answ_datetime_string = '2016.11.09-17.59.59'
#     test_datetime_string = trace.start_time.strftime("%Y.%m.%d-%H.%M.%S")
#     assert answ_datetime_string == test_datetime_string
#
#
# def test_get_duration(trace):
#     assert trace.duration == timedelta(seconds=3595, microseconds=995000)

# FileManager tests
@pytest.fixture()
def repository_path():
    return 'D:/JBP-Preprog-Recherche/Bonifacio_obspy/bonifacio_analysis/tests/data_test/Falaise_Janv2017/'


@pytest.fixture()
def file_name_regexp():
    return '*.C00.SAC'


@pytest.fixture()
def TraceManager(repository_path, file_name_regexp):
    return cd_model.TraceManager(repository_path, file_name_regexp)


def test_sort_traces1(TraceManager):
    assert len(TraceManager.non_merged_traces) == 4


def test_sort_traces2(TraceManager):
    sorted_but_not_merged_list = sorted(TraceManager.unsorted_traces, key=lambda trace: trace.stats.starttime)
    assert TraceManager.non_merged_traces == sorted_but_not_merged_list


def test_sort_traces3(TraceManager):
    assert len(TraceManager.sorted_traces) == 2
