import numpy as np
import pytest

from aprofiles.retrieval.ref_altitude import get_iref
from aprofiles import utils


@pytest.mark.parametrize("snr, accepted", [(2.0, True), (1.0, True), (0.5, False), (np.nan, False)])
def test_reference_snr_uses_selected_gate_and_original_signal(monkeypatch, snr, accepted):
    data = np.array([10., 9., 8., 7., 6., 5., 4., 3., 2., 1., 2., 3., 4., 5., 6., 7., 8., 9., 10.])
    indices = []

    def snr_at_gate(signal, iz, step):
        np.testing.assert_array_equal(signal, data)
        assert step == 4
        indices.append(iz)
        return snr

    monkeypatch.setattr(utils, "snr_at_iz", snr_at_gate)
    result = get_iref(data, 4, 15, 1.0)

    assert len(indices) == 1
    assert indices[0] == 6
    if accepted:
        assert result == indices[0]
    else:
        assert result is None
