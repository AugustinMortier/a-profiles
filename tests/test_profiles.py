import pytest
import aprofiles as apro


# arrange test
@pytest.fixture
def profiles():
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    return apro.reader.ReadProfiles(path).read()

# test class
class TestProfilesData:
    def test_snr(self, profiles):
        # test types
        assert type(profiles) is apro.profiles.ProfilesData
