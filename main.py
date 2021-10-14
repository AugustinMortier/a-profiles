#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Main

import aprofiles as apro
import numpy as np

#read some data
#path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
#path = "data/e-profile/2021/09/09/L2_0-20000-001492_A20210909.nc"
path = "examples/data/E-PROFILE/L2_0-20000-006735_A20210908.nc"
path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"


apro_reader = apro.reader.ReadProfiles(path)
profiles = apro_reader.read()

#signal to noise ratio
#profiles.snr(verbose=True)
#profiles.plot(var='snr',vmin=0, vmax=3, cmap='Greys_r')

#saturation
#profiles.plot(zmax=5000., log=True, vmin=1e-2, vmax=1e1)
#profiles.desaturate_below(z=4000., inplace=True)
#profiles.plot(zmax=5000., log=True, vmin=1e-2, vmax=1e1)

#extrapolation lowest layers
#profiles.plot(zmax=1000., log=True, vmin=1e-2, vmax=1e1)
#profiles.extrapolate_below(z=150, inplace=True)
#profiles.plot(zmax=1000., log=True, vmin=1e-2, vmax=1e1)

#detection
#profiles.foc(zmin_cloud=200)
#profiles.clouds(zmin=300, thr_noise=5, thr_clouds=4, verbose=True)
#profiles.pbl(zmin=200, zmax=3000, under_clouds=True, min_snr=2., verbose=True)

#plot image
#profiles.plot(zref='agl', zmax=6000., show_foc=True, show_clouds=False, show_pbl=False, log=True, vmin=1e-2, vmax=1e1)

#plot single profile
datetime = np.datetime64('2021-09-09T19:25:00')
datetime = np.datetime64('2021-09-09T21:20:00')
#datetime = np.datetime64('2021-09-09T10:25:00')
#profiles.plot(datetime=datetime, vmin=-1, vmax=10, zmax=12000, show_fog=True, show_clouds=True, show_pbl=True)

#klett inversion
#profiles.inversion(zmin=4000, zmax=6000, remove_outliers=True, method='forward', verbose=True)
#profiles.plot(var='ext', zmax=6000, vmin=0, vmax=5e-2)
#profiles.plot(var='aod')

##produce rayleigh profile
#altitude = profiles.data.altitude.data
#wavelength = profiles.data.l0_wavelength.data
#rayleigh = apro.rayleigh.RayleighData(altitude, T0=298, P0=1013, wavelength=wavelength);
#import matplotlib.pyplot as plt
#plt.plot(rayleigh.amol,altitude)
#plt.show()
