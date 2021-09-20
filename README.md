### A-Profiles

Python library for reading and processing [E-PROFILE](https://e-profile.eu/#/cm_profile) ceilometer data. This library is used by [V-Profiles](https://aerocom-vprofiles.met.no).

## Installation
`pip install aprofiles`

## Get started
```
#import library
import aprofiles as apro

#read NetCDF data
path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
apro_reader = apro.reader.ReadProfiles(path)
l2_data = apro_reader.read()

#plot Quick Look
apro_plotter = apro.plotter.Plotter(l2_data)
apro_plotter.plot('attenuated_backscatter_0',vmin=0, vmax=2, cmap='viridis')
``` 

<img src="examples/QL-AttenuatedBackscatter-A-20210907.png" title="Example of Attenuated Backscatter Signal" width="800"/>