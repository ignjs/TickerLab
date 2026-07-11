from datetime import datetime, timedelta

import polars as pl

from tickerlab.pivots.detector import detect_pivots


def test_detect_pivots_synthetic_wave():
    close = [1, 2, 3, 2, 1, 2, 3, 2, 1]
    bars = pl.DataFrame(
        {
            "ts": [datetime(2024, 1, 1) + timedelta(days=i) for i in range(9)],
            "symbol": ["AAA"] * 9,
            "timeframe": ["1d"] * 9,
            "open": close,
            "high": [x + 0.1 for x in close],
            "low": [x - 0.1 for x in close],
            "close": close,
            "adj_close": close,
            "volume": [1000] * 9,
        }
    )
    piv = detect_pivots(bars, window=1)
    assert piv.height >= 4
