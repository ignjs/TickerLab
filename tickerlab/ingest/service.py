from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import polars as pl

REQUIRED_OHLCV = ["ts", "open", "high", "low", "close", "volume"]


def normalize_bars(df: pl.DataFrame, symbol: str, timeframe: str) -> pl.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    aliases = {"date": "ts", "timestamp": "ts", "adj close": "adj_close", "adjclose": "adj_close"}
    renames: dict[str, str] = {}
    for lower, original in cols.items():
        if lower in aliases:
            renames[original] = aliases[lower]
        elif lower != original:
            renames[original] = lower
    if renames:
        df = df.rename(renames)

    missing = [c for c in REQUIRED_OHLCV if c not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")

    if "adj_close" not in df.columns:
        df = df.with_columns(pl.col("close").alias("adj_close"))

    return (
        df.select(["ts", "open", "high", "low", "close", "adj_close", "volume"])
        .with_columns(
            pl.col("ts").cast(pl.Datetime),
            pl.lit(symbol).alias("symbol"),
            pl.lit(timeframe).alias("timeframe"),
        )
        .sort("ts")
    )


def load_from_csv(path: str, symbol: str, timeframe: str) -> pl.DataFrame:
    df = pl.read_csv(path, try_parse_dates=True)
    return normalize_bars(df, symbol=symbol, timeframe=timeframe)


def load_synthetic(symbol: str, timeframe: str, bars: int = 800) -> pl.DataFrame:
    np.random.seed(7)
    start = date(2015, 1, 1)
    ts = [start + timedelta(days=i) for i in range(bars)]
    rets = np.random.normal(0.0004, 0.015, size=bars)
    close = 100 * np.cumprod(1 + rets)
    open_ = close * (1 + np.random.normal(0, 0.003, size=bars))
    spread = np.maximum(0.001, np.random.normal(0.01, 0.004, size=bars))
    high = np.maximum(open_, close) * (1 + spread)
    low = np.minimum(open_, close) * (1 - spread)
    volume = np.random.lognormal(14, 0.2, size=bars)
    raw = pl.DataFrame(
        {
            "ts": ts,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )
    return normalize_bars(raw, symbol=symbol, timeframe=timeframe)
