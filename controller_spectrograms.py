# -*- coding: utf-8 -*-
from collect_data import model as cd_model
from process_data import model as pd_model
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from datetime import datetime, timedelta
from matplotlib.ticker import FormatStrFormatter
import time
from obspy import read

# local settings
# stations_dict = {'SUT': ['Falaise_nov2016', '570009'],
                 # 'REF': ['Ref_nov2016', '570014'],
                 # }
# mother_repository = "D:/JBP-Preprog-Recherche/Bonifacio_obspy/data_test"


mother_repository = "//SRV51-NETAPP2/Data_RS/Bonifacio/Bonifacio-bdf-definitif"
stations_dict = {'SUT': ['Falaise_fev2017', '570009'],
                 'REF': ['Ref_fev2017', '570014'],
                 }

directions_dict = {'C00': 'Z', 'C01': 'N', 'C02': 'E'}

results_repository = "D:/JBP-Preprog-Recherche/Bonifacio_obspy/bonifacio_analysis/results"

reference_trace = read("D:/JBP-Preprog-Recherche/Bonifacio_obspy/bonifacio_analysis/tests/data_test/Falaise_nov2016/2016.11.06-23.59.59.AG.570009.00.C00.SAC")[0]

# --------------------------------------------------------------------------------------
# Script:
start_time = time.time()

maximum = 0
spectrograms = dict()
for station in ['Falaise_fev2017', 'Ref_fev2017']:
    for file_name, direction in directions_dict.items():

        print(f"Selecting {station} files in {direction} direction...")

        regexp = '*' + file_name + '.SAC'
        repository_path = mother_repository + '/' + station + '/'
        trace_manager = cd_model.TraceManager(repository_path, regexp)

        print(repository_path)
        print(regexp)

        print(f"Computing {station} spectrograms in {direction} direction...")

        hours_spectros = []
        freqs = None
        for trace in trace_manager.traces:
            if freqs is None:
                p_xx, freqs = pd_model.compute_decimated_spectrum(trace,
                                                                  reference_trace,
                                                                  decimal_value=5
                                                                  )
            else:
                p_xx = pd_model.compute_decimated_spectrum(trace,
                                                           reference_trace,
                                                           decimal_value=5
                                                           )[0]
            hours_spectros.append(p_xx)
        sp = np.transpose(np.array(hours_spectros))

        print(f"Saving {station}_{direction} files")

        save_file_sp = f"{results_repository}/{station}_{direction}_spectrogram.txt"
        np.savetxt(save_file_sp, sp, fmt='%1.4e')

        save_file_f = f"{results_repository}/{station}_{direction}_frequencies.txt"
        np.savez_compressed(save_file_sp, freqs, fmt='%1.4e')

        # TODO: need to compute maximums
        # maximum = max(np.max(sp), maximum)
        # computing max amplitude of all spectrograms
        # print("Maximal amplitude value: " + str(maximum))

        title = f"{station}_{direction}"
        print(f"Plotting {title}")

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        ax.set_title(title)
        ax.set_xlabel('Hours')
        ax.set_ylabel('Frequency (Hz)')

        x = np.arange(len(trace_manager.traces))
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

        plt.savefig(f"{results_repository}/{title}.png", format='png')


length = (time.time() - start_time)
length = length/60
print(f"total duration of the whole script : {length} min")

