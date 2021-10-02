import pytest
from aprofiles import reader
import xarray as xr
 
def test__ReadL2EPROFILE():
    """Check if the reading the fie returns a Dataset"""
    path = "examples/data/L2_0-20000-001492_A20210909.nc"
    l2_data = reader._ReadL2EPROFILE(path).read_file()
    assert type(l2_data) is xr.core.dataset.Dataset

