# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import FormatStrFormatter, FixedLocator, FixedFormatter

from process_data import model as pd_model
from weather_parsing import model as wp_model
from root import root

month_title = 'November_2016'
title = f"Ratio_Z_{month_title}"

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
ratio = pd_model.compute_ratio(sp_cliff, sp_ref, 0.05)

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

# list used in getting weather data
date = start_time.date()
date_list = [date]
while date < end_time.date():
    date += timedelta(days=1)
    date_list.append(date)


print('getting weather data')
data_file_name = root/f"weather_parsing/weather_data/{month_title}.weather"
try:
    wind, wind_gust, temp, rain = wp_model.read_weather_parser_file(date_list, data_file_name)
except FileNotFoundError:
    wp_model.save_weather_parser(date_list, data_file_name)
    print('data saved')
    wind, wind_gust, temp, rain = wp_model.read_weather_parser_file(date_list, data_file_name)


print('plotting')
fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4,
                                         ncols=1,
                                         sharex='all',
                                         sharey='none',
                                         gridspec_kw={'height_ratios': [3, 1, 1, 1]},
                                         figsize=(7, 9)
                                         )

ax1.pcolorfast(x,
               freqs,
               ratio,
               cmap='jet',
			   vmin=1,
			   vmax=15,
               #norm=colors.LogNorm(vmin=1, vmax=10),  # log scaling
               )

ax1.set_title(title)
ax1.set_ylabel('Freq (Hz)')

# ---> set the frequencies boundaries here <---
ax1.set_ylim([0.5, 8])
# ---> ################################### <---
ax1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
ax1.yaxis.set_minor_formatter(FormatStrFormatter('%.1f'))


ax2.set_ylabel('Wind (km/h)')
ax2.plot(np.arange(len(x)-1), wind, color='green')
ax2.set_ylim([0, 80])

ax3.set_ylabel('Temp (°C)')
ax3.plot(np.arange(len(x)-1), temp, color='red')
ax3.set_ylim([5, 25])

ax4.set_ylabel('Rain (mm/h)')
# TODO: check why rain is len(x)-2 instead of len(x)-1
ax4.plot(np.arange(len(x)-2), rain)
ax4.set_ylim([0, 10])

# setting shared x-axis
plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
name_list = [elt.strftime('%a %d %b') for elt in datetime_list]
ax1.xaxis.set_major_locator(FixedLocator(x[::60]))
ax1.xaxis.set_major_formatter(FixedFormatter(name_list[::60]))
ax1.set_xlim([x[0], x[-1]])
plt.xticks(rotation=70)

plt.tight_layout(pad=1, h_pad=0)
plt.savefig(f"{title}.png", format='png')
