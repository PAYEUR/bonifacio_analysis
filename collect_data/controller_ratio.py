# -*- coding: utf-8 -*-
from collect_data import model
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
from datetime import datetime, timedelta

mother_repository = 'D:/JBP-Preprog-Recherche/obspy/Bruit-de-fond'
stations_dict = {'SUT': ['Station-falaise', '570009'], 'REF': ['Station-reference', '570014']}
start = datetime(year=2016,
                 month=11,
                 day=6,
                 hour=23,
                 minute=59,
                 second=59)
end = datetime(year=2016,
               month=11,
               day=13,
               hour=22,
               minute=59,
               second=59)

time_list = model.perdelta(start, end, timedelta(hours=1))
timestamps = time_list
print("Number of investigated hours: " + str(len(timestamps)))


# --------------------------------------------------------------------------------------
# Script:

# load all data in one single python dict
print("Computing streams...")
streams = model.create_streams_dict(mother_repository, stations_dict, timestamps)

# compute ratios
print("Computing ratios:")

ratios = dict()

for index, direction in enumerate(['Z', 'N', 'E']):

    print("Computing ratio in %s direction..." % (direction,))
    # computing spectrograms
    sp1, freqs1 = model.compute_spectrogram('SUT' + ' ', index, streams, timestamps)
    sp2, freqs2 = model.compute_spectrogram('REF' + ' ', index, streams, timestamps)

    # computing ratio of spectrograms
    ratio = model.compute_ratio(sp1, sp2, 0.01)
    ratios[direction] = ratio, freqs1


# plotting
for index, direction in enumerate(['Z', 'N', 'E']):

    title = "SUT_over_REF_%s" % (direction,)
    print("Plotting " + title)

    ## get data and put it in the right way
    ratio, freqs = ratios[direction]
    data = np.transpose(ratio)

    ## plot spectrograms
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.set_title(title)
    ax.set_xlabel('Hours')
    ax.set_ylabel('Frequency (Hz)')

    x = np.arange(len(timestamps))
    y = freqs
    Z = data

    picture = ax.pcolorfast(x, y, Z,
                            cmap='jet',
                            vmin=0, vmax=10,  # linear scaling
                            )
    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax.yaxis.set_minor_formatter(FormatStrFormatter('%.0f'))
    plt.ylim(ymin=1, ymax=np.max(freqs))

    plt.colorbar(picture)

    plt.savefig(title + '.pdf', format='pdf')
