# -*- coding: utf-8 -*-
from collect_data import model
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from datetime import datetime, timedelta
from matplotlib.ticker import FormatStrFormatter
import time
from obspy import read

# local settings
# stations_dict = {'SUT': ['Station-falaise', '570009'],
                 # 'REF': ['Station-reference', '570014'],
                 # }
# mother_repository = "D:/JBP-Preprog-Recherche/Bonifacio_obspy/data_test"


mother_repository = "//SRV51-NETAPP2/Data_RS/Bonifacio/Bonifacio-bdf-definitif"
stations_dict = {'SUT': ['Falaise_fev2017', '570009'],
                 'REF': ['Ref_fev2017', '570014'],
                 }

results_repository = "D:/JBP-Preprog-Recherche/Bonifacio_obspy/bonifacio_analysis/results"

start = datetime(year=2017,
                 month=1,
                 day=31,
                 hour=23,
                 minute=59,
                 second=59)

end = datetime(year=2017,
               month=2,
               day=28,
               hour=22,
               minute=59,
               second=59)


reference_trace = read("D:/JBP-Preprog-Recherche/Bonifacio_obspy/bonifacio_analysis/tests/data_test/Station-falaise/2016.11.06-23.59.59.AG.570009.00.C00.SAC")[0]


time_list = model.perdelta(start, end, timedelta(hours=1))

# written by hand only for february
time_list[96] = time_list[95]
timestamps = time_list




print("Number of investigated hours: " + str(len(timestamps)))

# --------------------------------------------------------------------------------------
# Script:
start_time = time.time()

maximum = 0
spectrograms = dict()
for station in ['SUT', 'REF']:
    for direction in ['Z', 'N', 'E']:

        # compute spectrograms

        print(f"Computing {station} spectrogram in {direction} direction...")

        sp, freqs = model.compute_spectrogram(timestamps,
                                              mother_repository,
                                              stations_dict,
                                              station,
                                              direction,
                                              decimal_value=5,
                                              reference_trace=reference_trace)


        # TODO: need to compute maximums
        # maximum = max(np.max(sp), maximum)
        # computing max amplitude of all spectrograms
        # print("Maximal amplitude value: " + str(maximum))


        # plotting

        title = f"{station}_{direction}"
        print(f"Plotting {title}")

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        ax.set_title(title)
        ax.set_xlabel('Hours')
        ax.set_ylabel('Frequency (Hz)')

        x = np.arange(len(timestamps))
        y = freqs
        Z = sp

        picture = ax.pcolorfast(x, y, Z,
                                cmap='jet',
                                norm=colors.LogNorm(vmin=1e3, vmax=1e6),  # logarithmic scaling
                                )
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        ax.yaxis.set_minor_formatter(FormatStrFormatter('%.0f'))
        plt.ylim(ymin=1, ymax=np.max(freqs))

        cb = plt.colorbar(picture)
        cb.set_label('Arbitrary Units')

        plt.savefig(f"{results_repository}/{title}.pdf", format='pdf')


length = (time.time() - start_time)
length = length/60
print(f"total duration of the whole script : {length} min")

