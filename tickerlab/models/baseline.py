from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression


FEATURES = [
    "ret_1",
    "ret_5",
    "ema_ratio",
    "range_pct",
    "zscore_20",
    "vol_ratio_20",
    "rsi_14",
    "drawdown_20",
    "realized_vol_20",
]


def fit_logistic(X: np.ndarray, y: np.ndarray) -> LogisticRegression:
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    return model
