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


def test_sort_traces(TraceManager):
    sorted_traces = TraceManager.sort_traces()
    assert len(sorted_traces) == 4
    assert sorted_traces[2].stats.starttime < sorted_traces[3].stats.starttime
    # also check this condition (required but not coded):
    assert sorted_traces[2].stats.endtime < sorted_traces[3].stats.starttime


def test_merge_same_hour(TraceManager):
    unmerged_traces = TraceManager.sort_traces()
    merged_traces = TraceManager.merge_same_hour(unmerged_traces)
    assert len(merged_traces) == 2
    assert merged_traces[0].stats.starttime.minute == 40
    assert merged_traces[1].stats.starttime.minute == 16
