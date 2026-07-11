from tickerlab.validation.walkforward import walk_forward_indices


def test_walkforward_monotonic_indices():
    folds = list(walk_forward_indices(300, mode="rolling", train_size=100, test_size=20, n_splits=5, purge=2))
    assert len(folds) == 5
    for fold in folds:
        assert fold.train_idx.max() < fold.test_idx.min()
