import pytest
import weather_parsing.model as mp_model


@pytest.fixture()
def url_test():
    return 'http://www.infoclimat.fr/observations-meteo/archives/3/novembre/2016/bonifacio-cap-pertusato/07770.html'


@pytest.fixture()
def html_file_path_test():
    return 'tests/test.html'


@pytest.fixture()
def weather_parser(html_file_path_test):
    with open(html_file_path_test, 'r') as f:
        return mp_model.WeatherParser(f)


def test_temperature(weather_parser):
    temp_ref = [15.6, 15.6, 15.7, 15.7, 16.3, 16.9, 16.9, 17.2, 17.9, 18.2, 17.9, 18.5, 18.8, 18.8, 18.7,
                18.5, 18.1, 18.4, 18.2, 18.2, 17.9, 17.8, 18.0, 17.9]

    assert weather_parser.temp_list == temp_ref


def test_wind(weather_parser):
    wind_ref = [22.0, 22.0, 22.0, 22.0, 22.0, 29.0, 32.0, 32.0, 36.0, 40.0, 43.0, 47.0, 50.0, 50.0, 50.0,
                50.0, 47.0, 50.0, 47.0, 50.0, 47.0, 47.0, 40.0, 36.0]

    assert weather_parser.wind_list == wind_ref


def test_wind_gust(weather_parser):
    wind_gust_ref = [32.4, 28.8, 32.4, 32.4, 43.2, 46.8, 50.4, 50.4, 57.6, 61.2, 64.8, 72.0, 68.4, 75.6,
                     75.6, 72.0, 72.0, 64.8, 68.4, 68.4, 64.8, 61.2, 57.6, 54.0]

    assert weather_parser.wind_gust_list == wind_gust_ref


def test_time_slot(weather_parser):
    time_slots_ref = [0.0, 23.0, 22.0, 21.0, 20.0, 19.0, 18.0, 17.0, 16.0, 15.0, 14.0, 13.0, 12.0, 11.0,
                     10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]

    assert weather_parser.time_slots_list == time_slots_ref


def test_rain(weather_parser):
    rain_ref = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    assert weather_parser.rain_list == rain_ref