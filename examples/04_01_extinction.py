import aprofiles as apro

# read some data
path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
profiles = apro.reader.ReadProfiles(path).read()

# basic corrections
profiles.extrapolate_below(z=150, inplace=True)

# aerosol retrievals - forward inversion
profiles.inversion(
    zmin=4000, zmax=6000, remove_outliers=False, method="forward", verbose=True
)

# plot extinction profiles
profiles.plot(var="extinction", zmax=6000, vmin=0, vmax=5e-2)
