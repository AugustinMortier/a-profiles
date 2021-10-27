import aprofiles as apro

# read some data
path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
profiles = apro.reader.ReadProfiles(path).read()

# basic corrections
profiles.extrapolate_below(z=150., inplace=True)

# planetary boundary layer detection
profiles.pbl(zmin=200., zmax=3000., under_clouds=False, min_snr=2., verbose=True)

# plot image with pbl tracking
profiles.plot(zmax=6000., show_pbl=True, log=True, vmin=1e-2, vmax=1e1)
