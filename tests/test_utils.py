import aprofiles as apro


def test_get_true_indexes():
    true_indexes = apro.utils.get_true_indexes([True, False, True])
    # test values
    assert true_indexes == [0, 2]
