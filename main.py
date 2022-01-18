# @author Augustin Mortier
# @desc A-Profiles - Main

import numpy as np

import aprofiles as apro


def main(path):
    apro_reader = apro.reader.ReadProfiles(path)
    profiles = apro_reader.read()

    # signal to noise ratio
    # profiles.snr(verbose=True)
    # profiles.plot(var='snr',vmin=0, vmax=3, cmap='Greys_r')

    # saturation
    #profiles.plot(zmax=5000., log=True, vmin=1e-2, vmax=1e1, save_fig="docs/_static/images/saturated.png")
    #profiles.desaturate_below(z=4000., inplace=True)
    #profiles.plot(zmax=5000., log=True, vmin=1e-2, vmax=1e1, save_fig="docs/_static/images/desaturated.png")

    # gaussian filter
    #profiles.plot(log=True, vmin=1e-2, vmax=1e1, save_fig="docs/_static/images/attenuated_backscatter.png")
    #profiles.gaussian_filter(sigma=0.5, inplace=True)
    #profiles.plot(log=True, vmin=1e-2, vmax=1e1, save_fig="docs/_static/images/gaussian_filter.png")

    # extrapolation lowest layers
    # profiles.plot(zmax=1000., log=True, vmin=1e-2, vmax=1e1)
    #profiles.extrapolate_below(z=150, inplace=True)
    #profiles.plot(
    #    zref='agl', log=True, vmin=1e-2, vmax=1e1, 
    #    save_fig="docs/_static/images/QL-Oslo-20210909.png"
    #)
    #profiles.plot(zref='agl', show_foc=False, show_clouds=False, show_pbl=False, log=True, vmin=1e-2, vmax=1e1, zmax=6000.)
    # detection
    profiles.foc(zmin_cloud=200)
    profiles.clouds(zmin=300, thr_noise=5, thr_clouds=4, verbose=True)
    profiles.pbl(zmin=200, zmax=3000, under_clouds=False, min_snr=2., verbose=True)

    # plot image
    #profiles.plot(zref='agl', show_foc=False, show_clouds=True, show_pbl=False, log=True, vmin=1e-2, vmax=1e1, save_fig="docs/_static/images/clouds.png")
    #profiles.plot(zref='agl', show_foc=True, show_clouds=False, show_pbl=False, log=True, vmin=1e-2, vmax=1e1, save_fig="docs/_static/images/foc.png")
    profiles.plot(zref='agl', show_foc=False, show_clouds=False, show_pbl=True, log=True, vmin=1e-2, vmax=1e1, zmax=6000., save_fig="docs/_static/images/pbl.png")
    
    
    profiles.plot(
        zref='agl', show_foc=True, show_clouds=True, show_pbl=True, log=True, vmin=1e-2, vmax=1e1, 
        save_fig="docs/_static/images/QL-Fog&Clouds&PBL-Oslo-20210909.png"
    )
    
    # plot single profile
    # datetime = np.datetime64('2021-09-09T19:25:00')
    datetime = np.datetime64('2021-09-09T21:20:00')
    # datetime = np.datetime64('2021-09-09T10:25:00')
    profiles.plot(datetime=datetime, vmin=-1, vmax=10, zmax=12000, show_fog=False, show_clouds=False, show_pbl=False)#, save_fig="docs/_static/images/Profile-Oslo-20210909T212005.png")

    # aerosol inversion

    # backward
    # profiles.inversion(zmin=4000, zmax=6000, remove_outliers=False, method='backward', verbose=True)
    # profiles.plot(var='ext', zmax=6000, vmin=0, vmax=5e-2)
    # profiles.plot(var='aod')

    # forward
    profiles.inversion(zmin=4000, zmax=6000, remove_outliers=False, method="forward", verbose=True)
    profiles.plot(var="extinction", zmax=6000, vmin=0, vmax=5e-2)
    #profiles.plot(var="mass_concentration:dust", zmax=6000, vmin=0, vmax=5e-2)
    #profiles.plot('mass_concentration:dust', zmax=6000, vmin=0, vmax=100, cmap='Oranges')
    #profiles.plot('mass_concentration:urban', zmax=6000, vmin=0, vmax=100, cmap='Reds')
    # profiles.plot('pbl', ymin=0, ymax=3000)

    # # produce rayleigh profile
    # altitude = profiles.data.altitude.data
    # wavelength = profiles.data.l0_wavelength.data
    # rayleigh = apro.rayleigh_data.RayleighData(altitude, wavelength=wavelength, T0=298, P0=1013);
    # rayleigh.plot()
    # retrievals
    #profiles.write('testdir')

if __name__ == "__main__":
    # read some data
    path = "examples/data/E-PROFILE/L2_0-20000-006735_A20210908.nc"
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    main(path)
