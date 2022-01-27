import aprofiles as apro
import numpy as np
import pytest


# arrange test
@pytest.fixture
def step_model():
    wavelength = 1064.
    lidar_ratio = 50.
    noise = 0.
    model = apro.simulation.ext2back.ExtinctionToAttenuatedBackscatter('step', wavelength, lidar_ratio, noise)._model_extinction()
    return model

# test class
class TestExtinctionToAttenuatedBackscatter:
    def test__model_extinction(self, step_model):
        # test values
        assert np.nanmin(step_model.extinction_model[0,:]) == 0.0
        assert np.nanmax(step_model.extinction_model[0,:]) == 0.1
