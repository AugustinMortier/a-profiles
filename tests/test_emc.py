import aprofiles as apro
import numpy as np


# test class
class TestEMCData:
    def test_get_emc(self):
        emc_data = apro.emc.EMCData("urban", wavelength=1064.0).get_emc()
        # test values
        assert emc_data.aer_type == 'urban'
        assert emc_data.wavelength == 1064.0
        assert np.round(emc_data.conv_factor, 8) == 1.92e-06
        assert np.round(emc_data.emc, 4) == 0.3066

    def test_plot(self):
        # call plotting function
        fig = apro.emc.EMCData("urban", wavelength=1064.0).plot(show_fig=False)