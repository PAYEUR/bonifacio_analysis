# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import FormatStrFormatter, FixedLocator, FixedFormatter

from weather_parsing import model as wp_model
from root import root
import process_data.model as pd_model

title = "Falaise_Z_November_2016"

sp_file_path = root/'results/novembre2016/Falaise-nov2016_Z_spectrogram.txt'
frequ_file_path = root/'results/frequencies.txt'

start_time = datetime(year=2016, month=11, day=1, hour=0, minute=1)
end_time = datetime(year=2016, month=11, day=30, hour=23, minute=59)

# =================================================================================
print('loading spectrogram')
with open(frequ_file_path, 'rb') as f_f:
    freqs = np.loadtxt(f_f)

with open(sp_file_path, 'rb') as f_sp:
    sp = np.loadtxt(f_sp)

#sp = pd.read_csv(str(sp_file_path), sep=' ', header=None, dtype=np.float64).values
#freqs = pd.read_csv(str(frequ_file_path), sep=' ', header=None, dtype=np.float64).values.flatten()
#freqs2 = np.append(freqs, freqs[-1]+1e-4)

datetime_list = [start_time]
t = start_time
while t < end_time:
    t += timedelta(hours=1)
    datetime_list.append(t)


date = start_time.date()
date_list = [date]
while date < end_time.date():
    date += timedelta(days=1)
    date_list.append(date)


# get data
data_file_name = root/f"{title}.f"
try:
    wind, wind_gust, temp, rain = wp_model.read_weather_parser_file(date_list, data_file_name)
except FileNotFoundError:
    wp_model.save_weather_parser(date_list, data_file_name)
    print('data saved')
    wind, wind_gust, temp, rain = wp_model.read_weather_parser_file(date_list, data_file_name)


# plotting it
print('plotting')
fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4,
                                         ncols=1,
                                         sharex='all',
                                         sharey='none',
                                         gridspec_kw={'height_ratios': [3, 1, 1, 1]},
                                         figsize=(7, 9)
                                         )

x = np.arange(sp.shape[1]+1)

ax1.pcolorfast(x,
               freqs,
               sp,
               cmap='jet',
               norm=colors.LogNorm(vmin=1e3, vmax=1e6),  # logarithmic scaling
               )

ax1.set_title(title)
ax1.set_ylabel('Freq (Hz)')
ax1.set_yscale('log')
ax1.set_ylim([0.5, np.max(freqs)])
ax1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
ax1.yaxis.set_minor_formatter(FormatStrFormatter('%.1f'))

name_list = [elt.strftime('%a %d %b') for elt in datetime_list]
ax1.xaxis.set_major_locator(FixedLocator(x[::60]))
ax1.xaxis.set_major_formatter(FixedFormatter(name_list[::60]))


ax2.set_ylabel('Wind (km/h)')
ax2.plot(np.arange(len(x)), wind)
ax2.set_ylim([0, 100])

ax3.set_ylabel('Temp (°C)')
ax3.plot(np.arange(len(x)), temp)
ax3.set_ylim([-10, 50])

ax4.set_ylabel('Rain (mm/h)')
ax4.plot(np.arange(len(x)-1), rain)
ax4.set_ylim([0, 50])

plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
plt.xticks(rotation=70)
plt.tight_layout(pad=0.1, h_pad=0)
plt.savefig(f"{title}.png", format='png')
