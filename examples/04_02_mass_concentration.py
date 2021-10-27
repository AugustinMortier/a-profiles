import aprofiles as apro

# read some data
path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
profiles = apro.reader.ReadProfiles(path).read()

# basic corrections
profiles.extrapolate_below(z=150, inplace=True)

# aerosol retrievals - forward inversion
profiles.inversion(
    zmin=4000, zmax=6000, remove_outliers=True, method="forward", verbose=True
)

# plot mass concentration profiles im the case of desert dust
profiles.plot('mass_concentration:dust', zmax=6000, vmin=0, vmax=100, cmap='Oranges')
