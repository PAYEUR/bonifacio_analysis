# -*- coding: utf-8 -*-


def compute_ratio_spectrograms(indice, streams, timestamps):

    hour_spectros = []
    for timestamp in timestamps:
        keys = ['SUT ' + timestamp, 'REF ' + timestamp]

        spectro = []
        for i, key in enumerate(keys):
            # compute spectrums
            p_xx, freqs = model.compute_decimated_spectrum(streams[key].traces[indice], decimal_value=5)
            spectro.append(p_xx)

        # rapport
        ratio = model.compute_ratio(spectro[0], spectro[1], 0.01)
        hour_spectros.append(ratio)

    return np.array(hour_spectros), freqs


for indice, direction in enumerate(['Z', 'X', 'Y']):
    ### compute spectrograms
    print('computing spectrograms')
    array_hour_spectro = model.compute_spectrogram(indice, streams, timestamps)

    ### plot

    ## put data in the right way
    data = np.flipud(np.transpose(array_hour_spectro))

    ## plot one week spectro
    f, ax = plt.subplots()

    ax.imshow(data,
              interpolation='bilinear',
              extent=[frequencies[0], frequencies[-1], frequencies[0], frequencies[-1]],
              clim=(1, 2),
              )

    ax.set_xlabel('24 hours')
    ax.set_ylabel('Frequency (Hz)')

    # doesn't work since data non on a proper axis
    # plt.yscale('log')
    plt.savefig('results/one_day_spectros_' + direction + '.pdf', format='pdf')
    #plt.show()

    ## compare to 2D plot

    #plt.loglog(spectre.get_freq(), rapport)
    #plt.grid(True)
    #plt.xlabel('Frequency (Hz)')
    #plt.ylabel('Amplitude')
    #plt.savefig('last_spectro_' + direction + '.pdf', format='pdf')
    #plt.show()

# -----------------------------------------------------------------------------------
# controller function

def compute_spectrogram(timestamps,
                        mother_repository,
                        stations_dict,
                        station,
                        direction,
                        decimal_value,
                        reference_trace):
    """
    :param timestamps:
    :param mother_repository:
    :param stations_dict:
    :param station:
    :param direction:
    :param decimal_value
    :param reference_trace
    :return:
    """
    hours_spectros = []
    freqs = None

    for timestamp in timestamps:
        path = model.create_path(mother_repository, stations_dict, station, timestamp, direction)
        trace = read(path)[0]
        if freqs is None:
            p_xx, freqs = compute_decimated_spectrum(trace, reference_trace, decimal_value)
        else:
            p_xx = compute_decimated_spectrum(trace, reference_trace, decimal_value)[0]
        hours_spectros.append(p_xx)

    sp = np.transpose(np.array(hours_spectros))
    return sp, freqs



def test_compute_spectrogram(path_short_file,
                             timestamps,
                             mother_repository,
                             station_dict,
                             reference_trace,
                             decimal_value):

    # test compute_spectrogram function for station REF
    test_sp, test_freqs = pd_model.compute_spectrogram(timestamps,
                                                       mother_repository,
                                                       station_dict,
                                                       'REF',
                                                       'Z',
                                                       decimal_value,
                                                       reference_trace)


    # building data to test
    path0 = "tests/data_test/Ref_nov2016/2016.11.06-23.59.59.AG.570014.00.C00.SAC"
    path1 = "tests/data_test/Ref_nov2016/2016.11.09-17.59.59.AG.570014.00.C00.SAC"
    p_xx_0, freqs = pd_model.compute_decimated_spectrum(read(path0)[0], reference_trace, decimal_value)
    p_xx_1 = pd_model.compute_decimated_spectrum(read(path1)[0], reference_trace, decimal_value)[0]

    # testing spectrogram functions with data.
    # as it handle with np.arrays one have to use np.testing.assert_array_equal

    assert_array_equal(test_sp, np.transpose(np.array([p_xx_0, p_xx_1])))
    assert_array_equal(freqs, test_freqs)



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

def test_create_path(mother_repository, station_dict, timestamps, path_reference_file):

    built_path = cd_model.create_path(mother_repository,
                                      station_dict,
                                      'SUT',
                                      timestamps[0],
                                      'Z')
    st1 = read(built_path)
    st2 = read(path_reference_file)

    assert st1 == st2

class PerDeltaTest(unittest.TestCase):
    def setUp(self):
        self.start = datetime(year=2016,
                              month=11,
                              day=6,
                              hour=23,
                              minute=59,
                              second=59)
        self.end = datetime(year=2016,
                            month=11,
                            day=13,
                            hour=22,
                            minute=59,
                            second=59)

    self.time_list = cd_model.perdelta(self.start, self.end, timedelta(hours=1))

def test_perdelta(self):
    self.assertEqual(self.time_list[0], '2016.11.06-23')
    self.assertEqual(self.time_list[-1], '2016.11.13-22')

    @pytest.fixture()
    def mother_repository():
        return 'tests/data_test'

    @pytest.fixture()
    def station_dict():
        return {'SUT': ['Falaise_nov2016', '570009'],
                'REF': ['Ref_nov2016', '570014'],
                }

    @pytest.fixture()
    def timestamps():
        return ['2016.11.06-23', '2016.11.09-17']