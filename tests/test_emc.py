import aprofiles as apro


# test class
class TestEMCData:
    def test_get_emc(self):
        emc_data = apro.emc.EMCData("urban", wavelength=1064.0).get_emc()
        # test values
        assert emc_data.aer_type == 'urban'
        assert emc_data.wavelength == 1064.0
        assert emc_data.conv_factor == 1.9188709902928747e-06
        assert emc_data.emc == 0.3065528100082776
