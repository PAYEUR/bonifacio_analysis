# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors

from weather_parsing import model as wp_model
from root import root

title = "Falaise_Z_November_2016"

sp_file_path = root/'results/novembre2016/Falaise-nov2016_Z_spectrogram.txt'
frequ_file_path = root/'results/frequencies.txt'

start_time = datetime(year=2016, month=11, day=1, hour=0, minute=1)
end_time = datetime(year=2016, month=11, day=30, hour=23, minute=59)

# =================================================================================
print('loading spectrogram')
sp = pd.read_table(str(sp_file_path), delim_whitespace=True, header=None)

freqs = pd.read_csv(str(frequ_file_path), delim_whitespace=True, header=None)
# TODO: don't really see why there is shape problem.
freqs = np.append(freqs, freqs[-1])

x = []
t = start_time
while t < end_time:
    t += timedelta(hours=1)
    x.append(t)

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
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex='all', sharey='all')

ax1.set_ylabel('Frequency (Hz)')
ax1.pcolorfast(np.arange(len(x)+1), freqs, sp,
               cmap='jet',
               norm=colors.LogNorm(vmin=1e3, vmax=1e6),  # logarithmic scaling
               )

ax2.set_ylabel('Wind (km/h)')
ax2.plot(np.arange(len(x)), wind)
ax2.set_ylim([0, 100])

ax3.set_ylabel('Temp(°C)')
ax3.plot(np.arange(len(x)), temp)
ax3.set_ylim([-10, 50])

ax4.set_ylabel('Rain (mm/h')
# don't know why x.shape mismatches...
ax4.plot(np.arange(len(x)-1), rain)
ax4.set_ylim([0, 50])

fig.subplots_adjust(hspace=0)
plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
plt.title(title)
#plt.xlim(0, len(x)-1))
#plt.tight_layout()
plt.savefig(f"{title}.png", format='png')
