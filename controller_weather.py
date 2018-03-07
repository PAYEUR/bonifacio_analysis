# -*- coding: utf-8 -*-
import time
import random
from datetime import datetime, timedelta
from urllib import error

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

from weather_parsing import model as mp_model
from root import root

sp_file_path = root/'results/novembre2016/Falaise-nov2016_Z_spectrogram.txt'
frequ_file_path = root/'results/frequencies.txt'

sp = np.loadtxt(str(sp_file_path))
print('spectrogram loaded')
freqs = np.loadtxt(str(frequ_file_path))

start_time = datetime(year=2016, month=11, day=1, hour=0, minute=1)
end_time = datetime(year=2016, month=11, day=30, hour=23, minute=59)

x = [start_time]
t = start_time
while t < end_time:
    time += timedelta(hours=1)
    x.append(t)
print(x[:10])

date_list = []
date = start_time.date()
while date < end_time.date():
    date += timedelta(days=1)
    date_list.append(date)
date_list.append(end_time.date())
print(date_list[:10])

# get weather
# time_slot = []
wind = []
for date in date_list:
    print('connexion')
    time.sleep(random.uniform(0.5, 1.5))
    try:
        wp = mp_model.WeatherParser(date)
    except error.HTTPError:
        time.sleep(random.uniform(0.5, 1.5))
        try:
            wp = mp_model.WeatherParser(date)
        except error.HTTPError:
            print('steuplé!')
            time.sleep(random.uniform(20, 30))
            wp = mp_model.WeatherParser(date)
    # one considers that wp has finally been created
    finally:
        wind += reversed(wp.temp_list)

print(wind[:10])


# plotting it
fig = plt.figure(1)
ax1 = fig.add_subplot(2, 1, 1)
ax1.set_ylabel('Frequency (Hz)')

ax1.pcolorfast(np.arange(len(x)), freqs, sp,
               cmap='jet',
               norm=colors.LogNorm(vmin=1e3, vmax=1e6),  # logarithmic scaling
               )

ax2 = fig.add_subplot(2, 1, 2)
ax1.set_ylabel('Wind speed (km/h)')
ax1.plot(np.arange(len(x)), wind)

plt.savefig('toto.png', format='png')
