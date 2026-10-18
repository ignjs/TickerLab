from __future__ import annotations

import polars as pl

from tickerlab.models.baseline import FEATURES


def event_dataset(features: pl.DataFrame, events: pl.DataFrame, labels_event: pl.DataFrame, horizon: int = 5) -> pl.DataFrame:
    if events.height == 0 or labels_event.height == 0:
        return pl.DataFrame()
    target = labels_event.filter(pl.col("horizon") == horizon)
    base = events.join(features, left_on="ts_end", right_on="ts", how="left")
    return (
        base.join(target, on="event_id", how="inner")
        .drop_nulls(["forward_return"])
        .with_columns((pl.col("forward_return") > 0).cast(pl.Int8).alias("target"))
    )


def bar_dataset(features: pl.DataFrame, labels_bar: pl.DataFrame, horizon: int = 5) -> pl.DataFrame:
    return (
        features.join(labels_bar.select(["ts", f"forward_return_{horizon}"]), on="ts", how="left")
        .rename({f"forward_return_{horizon}": "forward_return"})
        .drop_nulls(["forward_return"])
        .with_columns((pl.col("forward_return") > 0).cast(pl.Int8).alias("target"))
    )


def as_xy(df: pl.DataFrame) -> tuple:
    sub = df.drop_nulls(FEATURES + ["target", "forward_return"])
    return sub.select(FEATURES).to_numpy(), sub["target"].to_numpy(), sub["forward_return"].to_numpy(), sub
