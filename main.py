#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Main

import aprofiles as apro
import numpy as np

#read some data
path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
#path = "data/e-profile/2021/09/09/L2_0-20000-001492_A20210909.nc"

apro_reader = apro.reader.ReadProfiles(path)
profiles = apro_reader.read()

#correct altitude
profiles.range_correction(var='attenuated_backscatter_0', inplace=True)

#extrapolate lowest layers where random signal is measured
profiles.extrapolation_lowest_layers(zmin=300, inplace=True)

#add some gaussian filtering
profiles.gaussian_filter(var='attenuated_backscatter_0', inplace=True)

#detect fog or condensation
profiles.detect_fog_or_condensation(zmin=300)#.quickplot(show_fog=True)

#detect clouds
profiles.detect_clouds(time_avg=15, zmin=300, thr_noise=5, thr_clouds=4).plot(show_clouds=True, log=True, vmin=1e0, vmax=1e5);

#plot single profile
profiles.plot(time=np.datetime64('2021-09-08T22:00:00'), show_fog=True, show_clouds=True, log=False)

##produce rayleigh profile
#altitude = profiles.data.altitude.data
#wavelength = profiles.data.l0_wavelength.data
#rayleigh = apro.rayleigh.Rayleigh(altitude, T0=298, P0=1013, wavelength=wavelength);
#import matplotlib.pyplot as plt
#plt.plot(rayleigh.amol,altitude)
#plt.show()
