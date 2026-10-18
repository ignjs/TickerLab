from __future__ import annotations

import polars as pl


def build_features(bars: pl.DataFrame) -> pl.DataFrame:
    out = bars.sort("ts").with_columns(
        (pl.col("close") / pl.col("close").shift(1) - 1).alias("ret_1"),
        (pl.col("close") / pl.col("close").shift(5) - 1).alias("ret_5"),
        (pl.col("close") / pl.col("close").shift(1)).log().alias("log_ret_1"),
        pl.col("close").ewm_mean(span=12).alias("ema_fast"),
        pl.col("close").ewm_mean(span=26).alias("ema_slow"),
        ((pl.col("high") - pl.col("low")) / pl.col("close")).alias("range_pct"),
        ((pl.col("open") / pl.col("close").shift(1)) - 1).alias("gap_pct"),
        ((pl.col("close") - pl.col("open")).abs() / (pl.col("high") - pl.col("low")).clip(1e-8, None)).alias("body_range"),
        ((pl.col("high") - pl.max_horizontal("open", "close")) / (pl.col("high") - pl.col("low")).clip(1e-8, None)).alias("upper_wick_ratio"),
        ((pl.min_horizontal("open", "close") - pl.col("low")) / (pl.col("high") - pl.col("low")).clip(1e-8, None)).alias("lower_wick_ratio"),
        (pl.col("volume") / pl.col("volume").rolling_mean(20).clip(1e-8, None)).fill_null(1.0).fill_nan(1.0).alias("vol_ratio_20"),
    ).with_columns(
        (pl.col("ema_fast") / pl.col("ema_slow").clip(1e-8, None)).fill_null(1.0).fill_nan(1.0).alias("ema_ratio"),
        ((pl.col("close") - pl.col("close").rolling_mean(20)) / pl.col("close").rolling_std(20).clip(1e-8, None)).fill_null(0.0).fill_nan(0.0).alias("zscore_20"),
        (pl.col("close") / pl.col("close").rolling_max(20).clip(1e-8, None) - 1).fill_null(0.0).fill_nan(0.0).alias("drawdown_20"),
        pl.col("range_pct").rolling_std(20).fill_null(0.0).fill_nan(0.0).alias("realized_vol_20"),
    )

    delta = pl.col("close").diff()
    gain = pl.when(delta > 0).then(delta).otherwise(0.0)
    loss = pl.when(delta < 0).then(-delta).otherwise(0.0)
    out = out.with_columns(
        gain.rolling_mean(14).alias("avg_gain_14"),
        loss.rolling_mean(14).alias("avg_loss_14"),
    ).with_columns(
        (100 - (100 / (1 + pl.col("avg_gain_14") / pl.col("avg_loss_14").clip(1e-8, None)))).alias("rsi_14")
    )

    return out.drop(["avg_gain_14", "avg_loss_14"])
