from datetime import datetime, timedelta

import polars as pl

from tickerlab.features.builder import build_features


def test_ema_ratio_scale_invariant():
    days = 61
    ts = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(days)]
    base = pl.DataFrame(
        {
            "ts": ts,
            "symbol": ["AAA"] * days,
            "timeframe": ["1d"] * days,
            "open": [100 + i for i in range(days)],
            "high": [101 + i for i in range(days)],
            "low": [99 + i for i in range(days)],
            "close": [100 + i for i in range(days)],
            "adj_close": [100 + i for i in range(days)],
            "volume": [1000 + i for i in range(days)],
        }
    )
    scaled = base.with_columns(
        open=pl.col("open") * 10,
        high=pl.col("high") * 10,
        low=pl.col("low") * 10,
        close=pl.col("close") * 10,
        adj_close=pl.col("adj_close") * 10,
    )
    a = build_features(base)
    b = build_features(scaled)
    diff = (a["ema_ratio"] - b["ema_ratio"]).abs().drop_nulls().max()
    assert diff < 1e-10
