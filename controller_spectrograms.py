# -*- coding: utf-8 -*-
from collect_data import model as cd_model
from process_data import model as pd_model
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from matplotlib.ticker import FormatStrFormatter
import time

# local settings
mother_repository = "D:/JBP-Preprog-Recherche/Bonifacio_obspy/Bruit-de-fond"
data_folders = ['Station-reference'] #'Station-falaise',

# prod settings
# mother_repository = '//SRV51-NETAPP2/Data_RS/Bonifacio/Bonifacio-bdf-definitif'

# data_folders = ['Falaise_Janv2017', 'Ref_janv2017',
#                 'Falaise_nov2016', 'Ref_nov2016',
#                 ]

# common settings
directions_dict = {'C00': 'Z', 'C01': 'N', 'C02': 'E'}

results_repository = 'D:/JBP-Preprog-Recherche/Bonifacio_obspy/bonifacio_analysis/results'

reference_file_path = 'D:/JBP-Preprog-Recherche/Bonifacio_obspy/bonifacio_analysis/tests/data_test/Falaise_nov2016/2016.11.06-23.59.59.AG.570009.00.C00.SAC'

# --------------------------------------------------------------------------------------
# Script:
start_time = time.time()

# maximum = 0
spectrograms = dict()
trace_processor = pd_model.TraceProcessor(reference_file_path,
                                          decimate_factor=5,
                                          freqmin=0.5,
                                          freqmax=15)

print(f"Saving frequencies file")
save_file_f = f"{results_repository}/frequencies.txt"
np.savetxt(save_file_f, trace_processor.filtred_and_decimated_ref_freqs, fmt='%1.4e')


for directory in data_folders:
    for file_reference, direction in directions_dict.items():

        title = f"{directory}_{direction}"

        # -------------------------------------------------------------------------
        # collecting and processing data
        print(f"Selecting {title} files...")

        regexp = f'*{file_reference}.SAC'
        repository_path = f'{mother_repository}/{directory}/'
        trace_manager = cd_model.TraceManager(repository_path, regexp)

        print(f"Computing {title} spectrogram...")

        # TODO: change hours_spectro into an iterable
        hours_spectros = []

        # TODO: change trace_manager.traces into an iterable
        for trace in trace_manager.traces:
            trace_processor.filter_trace(trace)
            p_xx = trace_processor.compute_decimated_spectrum(trace)[0]
            hours_spectros.append(p_xx)

        # TODO: check this cautiously
        sp = np.transpose(np.array(hours_spectros))
        del hours_spectros

        # -------------------------------------------------------------------------
        # saving data in files
        print(f"Saving {title} spectrogram file")

        save_file_sp = f"{results_repository}/{title}_spectrogram.txt"
        np.savetxt(save_file_sp, sp, fmt='%1.4e')

        # -------------------------------------------------------------------------
        # May need to compute maximums
        # maximum = max(np.max(sp), maximum)
        # computing max amplitude of all spectrograms
        # print("Maximal amplitude value: " + str(maximum))

        # -------------------------------------------------------------------------
        # Plotting figure
        print(f"Plotting {title}")

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        ax.set_title(title)
        ax.set_xlabel('Hours')
        ax.set_ylabel('Frequency (Hz)')

        x = np.arange(len(trace_manager.get_starttimes()))
        y = trace_processor.filtred_and_decimated_ref_freqs
        Z = sp

        picture = ax.pcolorfast(x, y, Z,
                                cmap='jet',
                                norm=colors.LogNorm(vmin=1e3, vmax=1e6),  # logarithmic scaling
                                )
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        ax.yaxis.set_minor_formatter(FormatStrFormatter('%.0f'))
        plt.ylim(ymin=1, ymax=np.max(y))

        cb = plt.colorbar(picture)
        cb.set_label('Arbitrary Units')

        plt.savefig(f"{results_repository}/{title}.png", format='png')


length = (time.time() - start_time)
length = length/60
print(f"total duration of the whole script : {length} min")

