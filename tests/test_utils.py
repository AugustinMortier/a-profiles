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

def file_exists():
    check = utils.file_exists("examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc")
    # test values
    assert check == True
