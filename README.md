# A-Profiles

Python library for reading and processing [E-PROFILE](https://e-profile.eu/#/cm_profile) ceilometer data. This library is used by [V-Profiles](https://aerocom-vprofiles.met.no).

## Documentation
The official documentation is available [here](https://a-profiles.readthedocs.io/).

## Installation
`pip install aprofiles`

## Get started
```
#import library
import aprofiles as apro

#read NetCDF data
path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
apro_reader = apro.reader.ReadProfiles(path)
profiles = apro_reader.read()
``` 

``` 
#apply range correction
profiles.range_correction(inplace=True)

#apply some gaussian filter for reducing the instrumental noise
profiles.gaussian_filter(sigma=0.5, inplace=True)

#plot Quick Look
profiles.quickplot(zmax=10000, vmin=1e1, vmax=1e5, log=True, cmap='viridis')
``` 
<img src="examples/QL-AttenuatedBackscatter-20210909.png" title="Example of Attenuated Backscatter Signal" width="1000"/>

```
#Add Fog or Condensation Markers
profiles.detect_fog_or_condensation(zmin=200)

#plot Quick Look
profiles.quickplot(zmax=10000, vmin=1e1, vmax=1e5, log=True, cmap='viridis')
```
<img src="examples/QL-AttenuatedBackscatter-Fog-20210909.png" title="Example of Attenuated Backscatter Signal" width="1000"/>