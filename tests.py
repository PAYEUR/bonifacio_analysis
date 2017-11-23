# -*- coding: utf-8 -*-
import pytest
from .collect_data.model import create_path
# ----------------------------------------------------
# switching to pytest
# using pytest-cov


@pytest.fixture()
def mother_repository():
    return 'data_test/Bruit-de-fond'


@pytest.fixture()
def station_dict():
    return {'SUT': ['Station-falaise', '570009'],
            'REF': ['Station-reference', '570014']}


@pytest.fixture()
def timestamp():
    return '2016.11.06-23.59.59'


def test_create_path():
    assert create_path(mother_repository,
                       station_dict,
                       'SUT',
                       timestamp,
                       'Z') \
           == "/data_test/Bruit-de-fond" \
           "Station-falaise/2016.11.06-23.59.59.AG.570009.00.C00.SAC"
