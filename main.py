#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles Plotter

from aprofiles import reader, plotter

path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
apro_reader = reader.ReadProfiles(path)
l2_data = apro_reader.read()

apro_plotter = plotter.Plotter(l2_data)
apro_plotter.plot('attenuated_backscatter_0',vmin=0, vmax=2, cmap='viridis')
