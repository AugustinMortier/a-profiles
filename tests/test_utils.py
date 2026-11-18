import numpy as np
import pytest
from aprofiles import utils


def test_get_true_indexes():
    true_indexes = utils.get_true_indexes([True, False, True])
    # test values
    assert true_indexes == [0, 2]

def test_make_mask():
    mask = utils.make_mask(5, [0, 2, 3])
    # test values
    assert len(mask) == 5
    assert len([i for i in mask if i]) == 3    

def test_file_exists():
    check = utils.file_exists("examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc")
    # test values
    assert check == True

def test_snr_at_iz():
    array = np.linspace(0,10)
    iz = 5
    step = 2
    snr = utils.snr_at_iz(array, iz, step)
    # test values
    assert snr == pytest.approx(np.mean(array[3:8]) / np.std(array[3:8]))


@pytest.mark.parametrize(
    "array, iz, step, expected",
    [
        ([100., 1., 2., 3., 4.], 2, 1, 2 / np.std([1., 2., 3.])),
        ([1., 2., 3.], 1, 1, 2 / np.std([1., 2., 3.])),
        ([1., np.nan, 3.], 1, 1, 2.),
        ([1., 2., 3.], 0, 1, np.nan),
        ([1., 2., 3.], 2, 1, np.nan),
        ([np.nan, np.nan, np.nan], 1, 1, np.nan),
        ([2., 2., 2.], 1, 1, np.nan),
        ([1., 2., 3.], 1, 0, np.nan),
        ([1., 2., 3.], 1, 2, np.nan),
    ],
)
def test_snr_at_iz_window_and_undefined_values(array, iz, step, expected):
    result = utils.snr_at_iz(np.array(array), iz, step)
    if np.isnan(expected):
        assert np.isnan(result)
    else:
        assert result == pytest.approx(expected)


@pytest.mark.parametrize("step", [-1, 1.5])
def test_snr_at_iz_rejects_invalid_step(step):
    with pytest.raises((TypeError, ValueError)):
        utils.snr_at_iz(np.array([1., 2., 3.]), 1, step)


@pytest.mark.parametrize("iz", [-1, 3])
def test_snr_at_iz_rejects_out_of_bounds_index(iz):
    with pytest.raises(IndexError):
        utils.snr_at_iz(np.array([1., 2., 3.]), iz, 1)

def test_gaussian():
    x = np.linspace(0,2)
    mu = 1
    sig = 0.1
    norm = 1
    gaussian = utils.gaussian(x, mu, sig, norm)
    # test values
    assert np.round(np.max(gaussian), 3) == 3.907
    assert np.round(np.std(gaussian), 3) == 1.069
