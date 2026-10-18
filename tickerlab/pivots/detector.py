from __future__ import annotations

import numpy as np
import polars as pl
from scipy.signal import argrelextrema


def detect_pivots(bars: pl.DataFrame, window: int = 3) -> pl.DataFrame:
    arr = bars["close"].to_numpy()
    highs = argrelextrema(arr, np.greater_equal, order=window)[0]
    lows = argrelextrema(arr, np.less_equal, order=window)[0]
    idx = np.concatenate([highs, lows])
    types = np.array(["high"] * len(highs) + ["low"] * len(lows))
    if len(idx) == 0:
        return pl.DataFrame({"ts": [], "symbol": [], "pivot_type": [], "price": [], "strength": [], "window": [], "smooth_level": []})
    piv = (
        bars.with_row_index("i")
        .filter(pl.col("i").is_in(idx.tolist()))
        .select("i", "ts", "symbol", pl.col("close").alias("price"))
        .join(pl.DataFrame({"i": idx, "pivot_type": types}), on="i", how="inner")
        .with_columns(
            pl.lit(float(window)).alias("strength"),
            pl.lit(window).alias("window"),
            pl.lit(0).alias("smooth_level"),
        )
        .drop("i")
        .sort("ts")
    )
    return piv
