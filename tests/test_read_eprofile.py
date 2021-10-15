import pytest
from aprofiles.io import read_eprofile
import xarray as xr
 
class TestReadEPROFILE:

    def __init__(self):
        self.path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"

    def test_read(self):
        data = ReadEPROFILE(self.path).read()
        assert type(data) is xr.core.dataset.Dataset 
    
    #"""Check if the reading the fie returns a Dataset"""
    #path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    #data = ReadEPROFILE(path).read()
    #assert type(data) is xr.core.dataset.Dataset
