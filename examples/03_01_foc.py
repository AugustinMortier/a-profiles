import aprofiles as apro

#read some data
path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
apro_reader = apro.reader.ReadProfiles(path)
profiles = apro_reader.read()

#basic corrections
profiles.extrapolate_below(z=150, inplace=True)

#foc detection
profiles.foc(zmin_cloud=200)

#plot image below 6000m with a highlight on foc
profiles.plot(show_foc=True, zmax=6000., vmin=1e-2, vmax=1e1, log=True)