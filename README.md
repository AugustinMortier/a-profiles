[![CI](https://github.com/AugustinMortier/A-Profiles/actions/workflows/ci.yml/badge.svg)](https://github.com/AugustinMortier/A-Profiles/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/a-profiles/badge/?version=latest)](https://a-profiles.readthedocs.io/en/latest/?badge=latest)

<img src="docs/_static/images/A-Profiles.png" width="200" style="margin: 20px 10px"/> 

Python library for reading and processing atmospheric profilers measurements. A-Profiles supports [E-PROFILE](https://e-profile.eu/#/cm_profile) ceilometer data. This library is used by [V-Profiles](https://vprofiles.met.no).

## <img src="docs/_static/images/book-solid.svg" height="20"/> Documentation
The official documentation is available [here](https://a-profiles.readthedocs.io/).

## <img src="docs/_static/images/cogs-solid.svg" height="20"/> Installation

### <img src="docs/_static/images/pip.svg" height="15"/> via *pip*
*aprofiles* is directly available on *pip*. This will install the latest released version of *aprofiles* and its depencencies.
    
`pip install aprofiles`

### <img src="docs/_static/images/github.svg" height="15"/> via *Git*
1. clone this repository

    `git clone https://github.com/AugustinMortier/A-Profiles.git`

2. installation
- with *pip* (>21.3)

    `pip install .`

- with *poetry*

    `poetry install`

## <img src="docs/_static/images/play-circle-solid.svg" height="20"/> Get started

### Reading Data
```
# import library
import aprofiles as apro

# read local NetCDF L2 data
path = "examples/data/L2_0-20000-006735_A20210908.nc"
profiles = apro.reader.ReadProfiles(path).read()
``` 

### Basic corrections and Image plotting
``` 
# extrapolate lowest layers for removing outliers
profiles.extrapolate_below(zmin=150, inplace=True)

# image plotting of backscatter signal in log scale
profiles.plot(zref='agl', vmin=1e-2, vmax=1e1, log=True)
``` 
<img src="docs/_static/images/QL-Oslo-20210909.png" title="Attenuated Backscatter Signal" width="800"/>


### Profiles Analysis
```
# fog/condensation detection
profiles.foc(zmin_cloud=200) 

# clouds detection
profiles.clouds(zmin=300, thr_noise=5, thr_clouds=4)

# planetary boundary layer
profiles.pbl(zmin=200, zmax=3000, under_clouds=True)
```

### Visualization

#### Image
```
# image plotting with additional retrievals
profiles.plot(show_fog=True, show_clouds=True, show_pbl=True, vmin=1e-2, vmax=1e1, log=True)
```
<img src="docs/_static/images/QL-Fog&Clouds&PBL-Oslo-20210909.png" title="Fog or Condensation and Clouds Detection" width="800"/>

##### Single Profile
```
# plot single profile at 21:20
datetime = np.datetime64('2021-09-09T21:20:00')
profiles.plot(datetime=datetime, vmin=-1, vmax=10, zmax=12000, show_clouds=True, show_pbl=True)
```
<img src="docs/_static/images/Profile-Oslo-20210909T212005.png" title="Single Profile View" width="400"/>

## <img src="docs/_static/images/balance-scale-solid.svg" height="20"/> License
[GPL-3.0](LICENSE).

## <img src="docs/_static/images/university-solid.svg" height="20"/> Support
*A-Profiles* is developed by [MET Norway](https://github.com/metno) and supported by [EUMETNET](https://www.eumetnet.eu/).
