import pytest
from aprofiles import reader


# arrange test
@pytest.fixture
def profiles():
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    return reader.ReadProfiles(path).read()

# test class
class ReadProfiles:
    def test_read(self):
        # test types
        assert type(profiles) is aprofiles.profiles.ProfilesData
