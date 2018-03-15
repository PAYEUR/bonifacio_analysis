# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import FormatStrFormatter, FixedLocator, FixedFormatter
from scipy.ndimage import gaussian_filter

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
sp_ref = pd_model.get_array(sp_reference_file_path)
sp_cliff = pd_model.get_array(sp_cliff_file_path)

print('computing ratio')
# TODO: rewrite ratio calls into a RatioManager class
# computing ratio
ratio = pd_model.compute_ratio(sp_cliff, sp_ref, 0.05)
# replace noisy columns
ratio = pd_model.remove_noisy_columns(ratio, 10)

# filter final data to improve readability
ratio = gaussian_filter(ratio, sigma=(7, 1))

# END TODO

freqs = pd_model.get_frequencies(freq_file_path)
# need to add 1 freq, to increase plot speed (something weird within pcolorfast function)
freqs = np.append(freqs, [freqs[-1]])

# lists used in plotting
datetime_list = [start_time]
t = start_time
while t < end_time:
    t += timedelta(hours=1)
    datetime_list.append(t)

x = np.arange(ratio.shape[1]+1)


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

name_list = [elt.strftime('%a %d %b') for elt in datetime_list]
ax1.xaxis.set_major_locator(FixedLocator(x[::60]))
ax1.xaxis.set_major_formatter(FixedFormatter(name_list[::60]))
ax1.set_xlim([x[0], x[-1]])
plt.xticks(rotation=70)

plt.tight_layout(pad=1, h_pad=0)
plt.savefig(f"{title}.png", format='png')
