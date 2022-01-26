import aprofiles as apro


def test_get_true_indexes():
    true_indexes = apro.utils.get_true_indexes([True, False, True])
    # test values
    assert true_indexes == [0, 2]

def test_make_mask():
    mask = apro.utils.make_mask(5, [0, 2, 3])
    # test values
    assert len(mask) == 5
    assert len([i for i in mask if i]) == 3    
