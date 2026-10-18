from datetime import datetime, timedelta

import polars as pl

from tickerlab.labels.builder import build_bar_labels


def test_forward_return_known_series():
    bars = pl.DataFrame(
        {
            "ts": [datetime(2024, 1, 1) + timedelta(days=i) for i in range(5)],
            "symbol": ["AAA"] * 5,
            "close": [100.0, 110.0, 121.0, 133.1, 146.41],
            "high": [101.0, 111.0, 122.0, 134.0, 147.0],
            "low": [99.0, 109.0, 120.0, 132.0, 145.0],
        }
    )
    bars = bars.with_columns(open=pl.col("close"), volume=pl.lit(1_000.0), adj_close=pl.col("close"), timeframe=pl.lit("1d"))
    out = build_bar_labels(bars, [1])
    assert abs(out[0, "forward_return_1"] - 0.10) < 1e-9
