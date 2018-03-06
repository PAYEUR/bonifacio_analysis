# -*- coding: utf-8 -*-
from collect_data import model as cd_model
from process_data import model as pd_model
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from matplotlib.ticker import FormatStrFormatter, FixedLocator, FixedFormatter
import time
from pathlib import Path


def root():
    return Path(__file__).parents[0]


# local settings
# mother_repository = "D:/JBP-Preprog-Recherche/Bonifacio_obspy/Bruit-de-fond"
# data_folders = ['Station-falaise']  # 'Station-reference',

# prod settings
mother_repository = '//SRV51-NETAPP2/Data_RS/Bonifacio/Bonifacio-bdf-definitif'

data_folders = ['Falaise-nov2016', 'Ref_nov2016',
                'Falaise_dec2016', 'Ref_dec2016',
                'Falaise_Janv2017', 'Ref_janv2017',
                'Falaise_fev2017', 'Ref_fev2017',
                'Falaise_mars2017', 'Ref_mars2017',
                'Falaise_av2017', 'Ref_av2017',
                'Falaise_mai2017', 'Ref_mai2017',
                ]

# common settings
directions_dict = {'C00': 'Z', 'C01': 'N', 'C02': 'E'}

results_repository = root()/'results'

reference_file_path = root()/'tests/data_test/Falaise_nov2016/2016.11.06-23.59.59.AG.570009.00.C00.SAC'

# --------------------------------------------------------------------------------------
# Script:
start_time = time.time()

spectrograms = dict()
trace_processor = pd_model.TraceProcessor(reference_file_path,
                                          decimate_factor=4,
                                          freqmin=0.5,
                                          freqmax=20)

print("Saving frequencies file")
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

        hours_spectros = []

        for trace in trace_manager.traces:
            trace_processor.filter_trace(trace)
            p_xx = trace_processor.compute_decimated_spectrum(trace)[0]
            hours_spectros.append(p_xx)

        sp = np.transpose(np.array(hours_spectros))
        x_list = trace_manager.get_starttimes() + [trace_manager.get_endtimes()[-1]]
        del hours_spectros
        del trace_manager

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
        # ax.set_xlabel('Hours')
        ax.set_ylabel('Frequency (Hz)')

        x = np.arange(len(x_list))
        y = trace_processor.filtred_and_decimated_ref_freqs
        Z = sp

        picture = ax.pcolorfast(x, y, Z,
                                cmap='jet',
                                norm=colors.LogNorm(vmin=1e3, vmax=1e6),  # logarithmic scaling
                                )

        # x axis:
        # after https://stackoverflow.com/questions/17129947/how-to-set-ticks-on-fixed-position-matplotlib
        name_list = [elt.strftime('%a %d %b') for elt in x_list]
        x_labels_interval = 5*24  # each 5 days
        ax.xaxis.set_major_locator(FixedLocator(x[::x_labels_interval]))
        ax.xaxis.set_major_formatter(FixedFormatter(name_list[::x_labels_interval]))
        plt.xticks(rotation=70)

        # y axis:
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax.yaxis.set_minor_formatter(FormatStrFormatter('%.1f'))
        plt.ylim(ymin=0.5, ymax=np.max(y))

        cb = plt.colorbar(picture)
        cb.set_label('Arbitrary Units')

        plt.tight_layout()
        plt.savefig(f"{results_repository}/{title}.png", format='png')


length = (time.time() - start_time)
length = length/60
print(f"total duration of the whole script : {length} min")

