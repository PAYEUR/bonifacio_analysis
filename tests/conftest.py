# -*- coding: utf-8 -*-
from datetime import datetime

from obspy import read
import pytest
import numpy as np

import process_data.model as pd_model
from root import root


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


@pytest.fixture(scope='module')
def short_psd(trace_processor, short_trace):
    freqs = trace_processor.filtred_and_decimated_ref_freqs

    trace = short_trace.copy()
    trace_processor.filter_trace(trace)
    pxx = trace_processor.compute_decimated_spectrum(trace)[0]
    # one single pxx in sp
    sp = np.transpose(np.array([pxx]))

    return freqs, sp


@pytest.fixture(scope='module')
def ratio_manager():
    # need to be consistent with short_trace
    start_time = datetime(year=2016, month=11, day=9, hour=18, minute=1)
    end_time = datetime(year=2016, month=11, day=9, hour=18, minute=59)
    frequencies_file_path = str(root / 'tests/data_test/freq.test')
    sp_cliff_file_path = str(root / 'tests/data_test/sp.test')

    return pd_model.RatioManager(sp_cliff_file_path=sp_cliff_file_path,
                                 sp_reference_file_path=sp_cliff_file_path,
                                 frequencies_file_path=frequencies_file_path,
                                 start_time=start_time,
                                 end_time=end_time)
