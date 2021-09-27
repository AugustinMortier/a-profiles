#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles Plotter

import aprofiles as apro

#read some data
path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
apro_reader = apro.reader.ReadProfiles(path)
profiles = apro_reader.read()
profiles.quickplot('attenuated_backscatter_0',vmin=0, vmax=2, cmap='viridis')

#produce rayleigh profile
altitude = profiles.data.altitude.data
wavelength = profiles.data.l0_wavelength.data
rayleigh = apro.rayleigh.Rayleigh(altitude, T0=298, P0=1013, wavelength=wavelength);
import matplotlib.pyplot as plt
plt.plot(rayleigh.amol,altitude)
plt.show()