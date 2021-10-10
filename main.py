#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Main

import aprofiles as apro
import numpy as np

#read some data
#path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
#path = "data/e-profile/2021/09/09/L2_0-20000-001492_A20210909.nc"
path = "examples/data/L2_0-20000-006735_A20210908.nc"
path = "examples/data/L2_0-20000-001492_A20210909.nc"


apro_reader = apro.reader.ReadProfiles(path)
profiles = apro_reader.read()

#extrapolate lowest layers where random signal is measured
profiles.extrapolate_below(zmin=150, inplace=True)#.plot(log=True, vmin=1e1, vmax=1e5)
profiles.plot(zref='agl', log=True, vmin=1e-2, vmax=1e1)

#detect fog or condensation
profiles.foc(zmin_cloud=200)

#detect clouds
profiles.clouds(zmin=300, thr_noise=5, thr_clouds=4, verbose=True)

#detect PBL
profiles.pbl(zmin=200, zmax=3000, under_clouds=True, verbose=True)

#plot image
profiles.plot(zref='agl', show_fog=True, show_clouds=True, show_pbl=True, log=True, vmin=1e-2, vmax=1e1)

#plot single profile
datetime = np.datetime64('2021-09-09T19:25:00')
profiles.plot(datetime=datetime, vmin=-1, vmax=10, zmax=12000, show_fog=True, show_clouds=True, show_pbl=True)

#klett inversion
#profiles.klett_inversion(zmin=4000, zmax=6000, remove_outliers=False, verbose=True)
#profiles.plot(var='ext', zmax=8000, vmax=5e-2)

##produce rayleigh profile
#altitude = profiles.data.altitude.data
#wavelength = profiles.data.l0_wavelength.data
#rayleigh = apro.rayleigh.Rayleigh(altitude, T0=298, P0=1013, wavelength=wavelength);
#import matplotlib.pyplot as plt
#plt.plot(rayleigh.amol,altitude)
#plt.show()
