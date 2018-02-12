# -*- coding: utf-8 -*-
import collect_data.model as cd_model
import pytest

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


def test_build_condition(TraceManager):
    sorted_traces = TraceManager.sort_traces()
    trace0 = sorted_traces[0]  # starttime: 1h40-30   endtime: 2h00-00
    trace1 = sorted_traces[1]  # starttime: 1h59-59   endtime: 2h04-56
    trace2 = sorted_traces[2]  # starttime: 2h16-51   endtime: 2h25-21

    # condition triggered
    # change in hour expected between trace0 and trace1
    assert cd_model.build_condition(True, trace0, trace1) is False
    assert cd_model.build_condition(True, trace1, trace2) is True
    assert cd_model.build_condition(True, trace0, trace2) is False

    # condition not triggered: check of absolute value of hour
    # change in hour expected between trace1 and trace2
    assert cd_model.build_condition(False, trace0, trace1) is True
    assert cd_model.build_condition(False, trace1, trace2) is False
    assert cd_model.build_condition(False, trace0, trace2) is False


def test_sort_traces(TraceManager):
    sorted_traces = TraceManager.sort_traces()
    assert len(sorted_traces) == 4
    assert sorted_traces[2].stats.starttime < sorted_traces[3].stats.starttime
    # also check this condition (required but not coded):
    assert sorted_traces[2].stats.endtime < sorted_traces[3].stats.starttime


def test_merge_same_hour_without_start_at_59(TraceManager):
    unmerged_traces = TraceManager.sort_traces()
    merged_traces = TraceManager.merge_same_hour(unmerged_traces, False)
    assert len(merged_traces) == 2
    assert merged_traces[0].stats.starttime.minute == 40
    assert merged_traces[1].stats.starttime.minute == 16


def test_merge_same_hour_with_start_at_59(TraceManager):
    unmerged_traces = TraceManager.sort_traces()
    merged_traces = TraceManager.merge_same_hour(unmerged_traces, True)
    print([(t.stats.starttime, t.stats.endtime) for t in merged_traces])
    assert len(merged_traces) == 2
    assert merged_traces[0].stats.starttime.minute == 40
    assert merged_traces[1].stats.starttime.minute == 59

