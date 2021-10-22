import aprofiles as apro

# path of the NetCDF file to be read
path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
profiles = apro.reader.ReadProfiles(path).read()

# gaussian filtering
profiles.gaussian_filtering(sigma=0.5, inplace=True)

# plot the attenuated backscatter profile
profiles.plot(log=True, vmin=1e-2, vmax=1e1)
