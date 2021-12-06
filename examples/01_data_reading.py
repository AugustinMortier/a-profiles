import aprofiles as apro

# path of the NetCDF file to be read
path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
# instantiate the ReadProfiles class with the file path
apro_reader = apro.reader.ReadProfiles(path)
# call the read method of the instance
profiles = apro_reader.read()

# plot the attenuated backscatter profile
profiles.plot(
    var="attenuated_backscatter_0", zref="agl", log=True, vmin=1e-2, vmax=1e1,
    save_fig="examples/images/attenuated_backscatter.png"
)
