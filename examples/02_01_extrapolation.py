import aprofiles as apro

#path of the NetCDF file to be read
path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
profiles = apro.reader.ReadProfiles(path).read()

#extrapolate lowest layers
profiles.extrapolate_below(z=150, inplace=True)

#plot the attenuated backscatter profile up to 1000m of altitude
profiles.plot(zref='agl', zmax=1000., log=True, vmin=1e-2, vmax=1e1)