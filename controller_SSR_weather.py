# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, FixedLocator, FixedFormatter
import pandas

from process_data import model as pd_model
from weather_parsing import model as wp_model
from root import root


month_title = 'November_2016'
title = f"SSR_{month_title}"

start_time = datetime(year=2016, month=11, day=1, hour=0, minute=1)
end_time = datetime(year=2016, month=11, day=30, hour=23, minute=59)
freq_file_path = root/'results/frequencies.txt'

# =================================================================================
# TODO: parallelize this
ratio_list = []
for direction in ('Z', 'N', 'E'):
    sp_reference_file_path = root / f'results/novembre2016/Ref_nov2016_{direction}_spectrogram.txt'
    sp_cliff_file_path = root / f'results/novembre2016/Falaise-nov2016_{direction}_spectrogram.txt'

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

    ratio_list.append(rm.ratio)

# TODO: parallelize this
print('getting weather data')
date = start_time.date()
date_list = [date]
while date < end_time.date():
    date += timedelta(days=1)
    date_list.append(date)

data_file_name = root/f"weather_parsing/weather_data/{month_title}.weather"
try:
    wind, wind_gust, temp, rain = wp_model.read_weather_parser_file(date_list, data_file_name)
except FileNotFoundError:
    wp_model.save_weather_parser(date_list, data_file_name)
    print('data saved')
    wind, wind_gust, temp, rain = wp_model.read_weather_parser_file(date_list, data_file_name)


print('plotting')
# lists used in plotting
freqs = pandas.read_csv(str(freq_file_path),
                        sep=' ',
                        header=None,
                        dtype=np.float64).values.flatten()
freqs = np.append(freqs, freqs[-1])

datetime_list = []
t = start_time
while t < end_time:
    datetime_list.append(t)
    t += timedelta(hours=1)

x = np.arange(len(datetime_list) + 1)


# plot
fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(nrows=6,
                                                   ncols=1,
                                                   sharex='all',
                                                   sharey='none',
                                                   gridspec_kw={'height_ratios': [3, 3, 3, 1, 1, 1]},
                                                   figsize=(7, 15)
                                                   )

for ax, ratio, direction in zip((ax1, ax2, ax3),
                                ratio_list,
                                ('Z', 'N', 'E')):

    ax.pcolorfast(x,
                  freqs,
                  ratio,
                  cmap='jet',
                  vmin=1,
                  vmax=15,
                  )

    ax.set_ylabel(f'Freq (Hz), direction {direction}')

    # ---> set the frequencies boundaries here <---
    ax.set_ylim([0.5, 15])
    # ---> ################################### <---
    # ---> ################################### <---
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.yaxis.set_minor_formatter(FormatStrFormatter('%.1f'))

ax1.set_title(title)

ax4.set_ylabel('Wind (km/h)')
ax4.plot(np.arange(len(x)-1), wind, color='green')
ax4.set_ylim([0, 90])

ax5.set_ylabel('Temp (°C)')
ax5.plot(np.arange(len(x)-1), temp, color='red')
ax5.set_ylim([0, 30])

ax6.set_ylabel('Rain (mm/h)')
# TODO: check why rain is len(x)-2 instead of len(x)-1
try:
    ax6.plot(np.arange(len(x)-1), rain)
except ValueError:
    ax6.plot(np.arange(len(x)-2), rain)
ax6.set_ylim([0, 15])

# setting shared x-axis
plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
name_list = [elt.strftime('%a %d %b') for elt in datetime_list]
ax1.xaxis.set_major_locator(FixedLocator(x[::60]))
ax1.xaxis.set_major_formatter(FixedFormatter(name_list[::60]))
ax1.set_xlim([x[0], x[-1]])
plt.xticks(rotation=70)

plt.tight_layout(pad=1, h_pad=0)
plt.savefig(f"{title}.png", format='png')
