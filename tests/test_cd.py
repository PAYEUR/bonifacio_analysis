# -*- coding: utf-8 -*-
import collect_data.model as cd_model
import pytest


# FileManager tests
@pytest.fixture()
def repository_path():
    return 'tests/data_test/Falaise_Janv2017/'


@pytest.fixture()
def file_name_regexp():
    return '*.C00.SAC'


@pytest.fixture()
def trace_manager_start_at_59(repository_path, file_name_regexp):
    return cd_model.TraceManager(repository_path, file_name_regexp)


@pytest.fixture()
def trace_manager_no_start_at_59(repository_path, file_name_regexp):
    return cd_model.TraceManager(repository_path, file_name_regexp, start_at_59=False)


def test_build_condition(trace_manager_start_at_59, trace_manager_no_start_at_59):

    # one creates test traces
    sorted_traces = trace_manager_start_at_59.sort_traces()
    trace0 = sorted_traces[0]  # starttime: 1h40-30   endtime: 2h00-00
    trace1 = sorted_traces[1]  # starttime: 1h59-59   endtime: 2h04-56
    trace2 = sorted_traces[2]  # starttime: 2h16-51   endtime: 2h25-21

    # condition triggered
    # change in hour expected between trace0 and trace1
    assert trace_manager_start_at_59.is_same_hour(trace0, trace1) is False
    assert trace_manager_start_at_59.is_same_hour(trace1, trace2) is True
    assert trace_manager_start_at_59.is_same_hour(trace0, trace2) is False

    # condition not triggered: check of absolute value of hour
    # change in hour expected between trace1 and trace2
    assert trace_manager_no_start_at_59.is_same_hour(trace0, trace1) is True
    assert trace_manager_no_start_at_59.is_same_hour(trace1, trace2) is False
    assert trace_manager_no_start_at_59.is_same_hour(trace0, trace2) is False


def test_sort_traces(trace_manager_start_at_59):
    sorted_traces = trace_manager_start_at_59.sort_traces()
    assert len(sorted_traces) == 4
    assert sorted_traces[2].stats.starttime < sorted_traces[3].stats.starttime
    # also check this condition (required but not coded):
    assert sorted_traces[2].stats.endtime < sorted_traces[3].stats.starttime


def test_merge_same_hour_without_start_at_59(trace_manager_no_start_at_59):
    merged_traces = trace_manager_no_start_at_59.traces
    assert len(merged_traces) == 2
    assert merged_traces[0].stats.starttime.minute == 40
    assert merged_traces[1].stats.starttime.minute == 16


def test_merge_same_hour_with_start_at_59(trace_manager_start_at_59):
    merged_traces = trace_manager_start_at_59.traces
    assert len(merged_traces) == 2
    assert merged_traces[0].stats.starttime.minute == 40
    assert merged_traces[1].stats.starttime.minute == 59

