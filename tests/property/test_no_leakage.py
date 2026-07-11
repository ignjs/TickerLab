from hypothesis import given, strategies as st

from tickerlab.validation.walkforward import walk_forward_indices


@given(
    n_rows=st.integers(min_value=120, max_value=1500),
    train_size=st.integers(min_value=50, max_value=300),
    test_size=st.integers(min_value=10, max_value=50),
    purge=st.integers(min_value=0, max_value=5),
)
def test_no_temporal_leakage(n_rows: int, train_size: int, test_size: int, purge: int):
    folds = list(walk_forward_indices(n_rows, mode="rolling", train_size=train_size, test_size=test_size, n_splits=3, purge=purge))
    for fold in folds:
        assert fold.train_idx.max() < fold.test_idx.min()
