# -*- coding: utf-8 -*-
from datetime import datetime

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import FormatStrFormatter, FixedLocator, FixedFormatter


from process_data import model as pd_model
from root import root

month_title = 'November_2016'
title = f"Ratio_Z_{month_title}_filtred_with_columns"

sp_reference_file_path = root/'results/novembre2016/Ref_nov2016_Z_spectrogram.txt'
sp_cliff_file_path = root/'results/novembre2016/Falaise-nov2016_Z_spectrogram.txt'
freq_file_path = root/'results/frequencies.txt'

start_time = datetime(year=2016, month=11, day=1, hour=0, minute=1)
end_time = datetime(year=2016, month=11, day=30, hour=23, minute=59)

# =================================================================================
print('loading cliff and ref spectrograms')
rm = pd_model.RatioManager(sp_cliff_file_path,
                           sp_reference_file_path,
                           freq_file_path,
                           start_time,
                           end_time,
                           )

print('filtering ratio')
# replace noisy columns
rm.remove_noisy_columns(10)
# filter final data to improve readability
rm.smooth((7, 1))

ratio = rm.ratio

# lists used in plotting
freqs = np.append(rm.frequencies, rm.frequencies[-1])
x = np.arange(len(rm.datetime_list) + 1)


print('plotting')
fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)

pict = ax1.pcolorfast(x,
                      freqs,
                      ratio,
                      cmap='jet',
                      vmin=1,
                      vmax=15,
                      # norm=colors.LogNorm(vmin=1, vmax=10),  # log scaling
                      )

cb = plt.colorbar(pict)

ax1.set_title(title)
ax1.set_ylabel('Freq (Hz)')

# ---> set the frequencies boundaries here <---
ax1.set_ylim([0.5, 8])
# ---> ################################### <---
ax1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
ax1.yaxis.set_minor_formatter(FormatStrFormatter('%.1f'))

name_list = [elt.strftime('%a %d %b') for elt in rm.datetime_list]
ax1.xaxis.set_major_locator(FixedLocator(x[::60]))
ax1.xaxis.set_major_formatter(FixedFormatter(name_list[::60]))
ax1.set_xlim([x[0], x[-1]])
plt.xticks(rotation=70)

plt.tight_layout(pad=1, h_pad=0)
plt.savefig(f"{title}.png", format='png')
