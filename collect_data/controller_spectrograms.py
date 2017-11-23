# -*- coding: utf-8 -*-
from collect_data import model
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from datetime import datetime, timedelta
from matplotlib.ticker import FormatStrFormatter, NullLocator

mother_repository = 'D:/JBP-Preprog-Recherche/obspy/Bruit-de-fond'
stations_dict = {'SUT': ['Station-falaise', '570009'],
                 'REF': ['Station-reference', '570014'],
                 }
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

# compute spectrograms
print("Computing spectrograms:")
maximum = 0
spectrograms = dict()
for station in ['SUT', 'REF']:
    for index, direction in enumerate(['Z', 'N', 'E']):

        print("Computing %s spectrograms in %s direction..." % (station, direction))
        sp, freqs = model.compute_spectrogram(station + ' ', index, streams, timestamps)
        spectrograms[station, direction] = sp, freqs

        maximum = max(np.max(sp), maximum)

# computing max amplitude of all spectrograms
print("Maximal amplitude value: " + str(maximum))

# plotting
for station in ['SUT', 'REF']:
    for index, direction in enumerate(['Z', 'N', 'E']):

        title = "%s_%s" % (station, direction)
        print("Plotting " + title)

        # get data and put it in the right way
        sp, freqs = spectrograms[station, direction]
        data = np.transpose(sp)

        # plot spectrograms
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
                                norm=colors.LogNorm(vmin=maximum/100000, vmax=maximum/10),  # logarithmic scaling
                                )
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        ax.yaxis.set_minor_formatter(FormatStrFormatter('%.0f'))
        plt.ylim(ymin=1, ymax=np.max(freqs))

        cb = plt.colorbar(picture)
        cb.set_label('Arbitrary Units')

        plt.savefig(title + 'normalized.pdf', format='pdf')
