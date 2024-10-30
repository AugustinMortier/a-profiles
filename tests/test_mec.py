import aprofiles as apro
import numpy as np


# test class
class TestMECData:
    def test_get_mec(self):
        mec_data = apro.mec.MECData("urban", wavelength=1064.0).get_mec()
        # test values
        assert mec_data.aer_type == 'urban'
        assert mec_data.wavelength == 1064.0
        assert np.round(mec_data.conv_factor, 8) == 1.92e-06
        assert np.round(mec_data.mec, 4) == 0.3066

    def test_plot(self):
        # call plotting function
        fig = apro.mec.MECData("urban", wavelength=1064.0).plot(show_fig=False)