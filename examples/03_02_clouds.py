import aprofiles as apro

# read some data
path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
profiles = apro.reader.ReadProfiles(path).read()

# basic corrections
profiles.extrapolate_below(z=150., inplace=True)

# clouds detection
profiles.clouds(zmin=300., thr_noise=5., thr_clouds=4., verbose=True)

# plot image with clouds
profiles.plot(show_clouds=True, log=True, vmin=1e-2, vmax=1e1)
