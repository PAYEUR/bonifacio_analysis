# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

from weather_parsing import model as wp_model
from root import root

sp_file_path = root/'results/novembre2016/Falaise-nov2016_Z_spectrogram.txt'
frequ_file_path = root/'results/frequencies.txt'

sp = np.loadtxt(str(sp_file_path))
print('spectrogram loaded')

freqs = np.loadtxt(str(frequ_file_path))
# TODO: don't really see why there is shape problem.
freqs = np.append(freqs, freqs[-1])

start_time = datetime(year=2016, month=11, day=1, hour=0, minute=1)
end_time = datetime(year=2016, month=11, day=30, hour=23, minute=59)

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
data_file_name = root/'data.f'
try:
    wind, wind_gust, temp, rain = wp_model.read_weather_parser_file(date_list, data_file_name)
except FileNotFoundError:
    wp_model.save_weather_parser(date_list, data_file_name)
    print('data saved')
    wind, wind_gust, temp, rain = wp_model.read_weather_parser_file(date_list, data_file_name)


# plotting it
fig = plt.figure(1)
plt.title("Falaise_Z November 2016")

ax1 = fig.add_subplot(4, 1, 1)
ax1.set_ylabel('Frequency (Hz)')
ax1.pcolorfast(np.arange(len(x)+1), freqs, sp,
               cmap='jet',
               norm=colors.LogNorm(vmin=1e3, vmax=1e6),  # logarithmic scaling
               )

ax2 = fig.add_subplot(4, 1, 2)
ax2.set_ylabel('Wind speed (km/h)')
ax2.plot(np.arange(len(x)), wind)
ax2.axis([0, len(x), 0, 100])

ax3 = fig.add_subplot(4, 1, 3)
ax3.set_ylabel('Temperature (°C)')
ax3.plot(np.arange(len(x)), temp)
ax3.axis([0, len(x), -10, 50])

ax4 = fig.add_subplot(4, 1, 4)
ax4.set_ylabel('Rain (mm/h')
ax4.plot(np.arange(len(x)), rain)
ax4.axis([0, len(x), 0, 50])

plt.savefig('toto.png', format='png')
