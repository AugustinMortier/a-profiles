import aprofiles as apro
import numpy as np


# test class
class TestSizeDistributionData:
    def test_get_sd(self):
        sd_data = apro.size_distribution.SizeDistributionData("urban").get_sd()
        # test values
        assert np.round(np.nanmean(sd_data.vsd), 5) == 0.0029
        assert np.round(np.nanmean(sd_data.nsd), 5) == 1.98547

    def test_plot(self):
        # call plotting method
        fig = apro.size_distribution.SizeDistributionData("urban").plot(show_fig=False)
