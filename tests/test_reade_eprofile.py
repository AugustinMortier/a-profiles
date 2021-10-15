import pytest
from aprofiles import read_eprofile
import xarray as xr
 
def test__ReadEPROFILE():
    """Check if the reading the fie returns a Dataset"""
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    data = reader._ReadL2EPROFILE(path).read_file()
    assert type(data) is xr.core.dataset.Dataset

