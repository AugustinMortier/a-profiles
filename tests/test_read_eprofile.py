import pytest
from aprofiles.io import read_eprofile
import xarray as xr

# arrange test
@pytest.fixture
def path():
    return "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"


# test class
class TestReadEPROFILE:
    def test_read(self, path):
        data = read_eprofile.ReadEPROFILE(path).read()
        assert type(data) is xr.core.dataset.Dataset
