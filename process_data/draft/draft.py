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

