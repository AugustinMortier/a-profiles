import aprofiles as apro
import numpy as np


# test class
class TestRayleighData:
    def test_get_optics_in_std_atmo(self):
        altitude = np.arange(15, 15000, 15)
        rayleigh_data = apro.rayleigh.RayleighData(altitude, T0=298, P0=1013, wavelength=1064.).get_optics_in_std_atmo()
        # test values
        assert np.round(rayleigh_data.cross_section*1e28, 3) == 2.817
        assert np.round(rayleigh_data.tau, 5) == 0.00583
