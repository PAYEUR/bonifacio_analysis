# -*- coding: utf-8 -*-
import process_data.model as pd_model
from obspy import read
import pytest


@pytest.fixture(scope='module')
def short_trace():
    return read('tests/data_test/Ref_nov2016/2016.11.09-17.59.59.AG.570014.00.C00.SAC')[0]


@pytest.fixture(scope='module')
def long_trace():
    return read('tests/data_test/Falaise_nov2016/2016.11.09-17.59.59.AG.570009.00.C00.SAC')[0]


@pytest.fixture(scope='module')
def decimate_factor():
    return 15  # in order to run tests faster. Need to be smaller than 16


@pytest.fixture(scope='module')
def reference_file_path():
    return 'tests/data_test/Falaise_nov2016/2016.11.06-23.59.59.AG.570009.00.C00.SAC'


@pytest.fixture(scope='module')
def trace_processor(reference_file_path, decimate_factor):
    return pd_model.TraceProcessor(reference_file_path,
                                   decimate_factor,
                                   0.5,
                                   15)
