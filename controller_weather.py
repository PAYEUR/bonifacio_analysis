# -*- coding: utf-8 -*-
import time
import random
import pickle
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
print(sp.shape)
freqs = np.loadtxt(str(frequ_file_path))
# TODO: don't really see why there is shape problem.
freqs = np.append(freqs, freqs[-1])
print(freqs.shape)

start_time = datetime(year=2016, month=11, day=1, hour=0, minute=1)
end_time = datetime(year=2016, month=11, day=30, hour=23, minute=59)

x = []
t = start_time
while t < end_time:
    t += timedelta(hours=1)
    x.append(t)
print(x[:10])
print(len(x))

date = start_time.date()
date_list = [date]
while date < end_time.date():
    date += timedelta(days=1)
    date_list.append(date)

print(date_list[:10])
print(len(date_list))

# get wind
try:
    with open('wind.f', 'rb') as f:
        wind = pickle.load(f)
except FileNotFoundError:
    wind = []
    for date in date_list:
        print('connexion')
        time.sleep(random.uniform(1, 2))
        try:
            wp = mp_model.WeatherParser(date)
        except error.HTTPError:
            time.sleep(random.uniform(5, 10))
            try:
                wp = mp_model.WeatherParser(date)
            except error.HTTPError:
                print('steuplaye!')
                time.sleep(random.uniform(20, 30))
                wp = mp_model.WeatherParser(date)
        # one considers that wp has finally been created
        finally:
            wind += reversed(wp.wind_list)
            pickle.dump(wind, 'wind.f')


print(wind[:10])
print(len(wind))


# plotting it
fig = plt.figure(1)
ax1 = fig.add_subplot(2, 1, 1)
ax1.set_ylabel('Frequency (Hz)')

ax1.pcolorfast(np.arange(len(x)+1), freqs, sp,
               cmap='jet',
               norm=colors.LogNorm(vmin=1e3, vmax=1e6),  # logarithmic scaling
               )

ax2 = fig.add_subplot(2, 1, 2)
ax1.set_ylabel('Wind speed (km/h)')
ax1.plot(np.arange(len(x)), wind)

plt.savefig('toto.png', format='png')
