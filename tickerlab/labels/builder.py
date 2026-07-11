from __future__ import annotations

import polars as pl


def build_bar_labels(bars: pl.DataFrame, horizons: list[int], threshold: float = 0.02) -> pl.DataFrame:
    df = bars.select("ts", "symbol", "close", "high", "low")
    exprs = []
    for h in horizons:
        exprs.extend(
            [
                (pl.col("close").shift(-h) / pl.col("close") - 1).alias(f"forward_return_{h}"),
                ((pl.col("close").shift(-h) / pl.col("close") - 1) > threshold).cast(pl.Int8).alias(f"hit_up_{h}"),
                ((pl.col("close").shift(-h) / pl.col("close") - 1) < -threshold).cast(pl.Int8).alias(f"hit_down_{h}"),
                (pl.col("high").rolling_max(h).shift(-h + 1) / pl.col("close") - 1).alias(f"max_favorable_{h}"),
                (pl.col("low").rolling_min(h).shift(-h + 1) / pl.col("close") - 1).alias(f"max_adverse_{h}"),
                pl.col("close").pct_change().rolling_std(h).shift(-h + 1).alias(f"realized_vol_future_{h}"),
            ]
        )
    return df.with_columns(*exprs)


def build_event_labels(bars: pl.DataFrame, events: pl.DataFrame, horizons: list[int], threshold: float = 0.02) -> pl.DataFrame:
    if events.height == 0:
        return pl.DataFrame({"event_id": [], "horizon": [], "forward_return": [], "hit_up": [], "hit_down": [], "max_favorable": [], "max_adverse": [], "realized_vol_future": []})

    bar_labels = build_bar_labels(bars, horizons, threshold)
    rows: list[dict] = []
    for ev in events.iter_rows(named=True):
        ts_end = ev["ts_end"]
        bar = bar_labels.filter(pl.col("ts") == ts_end)
        if bar.height == 0:
            continue
        for h in horizons:
            rows.append(
                {
                    "event_id": ev["event_id"],
                    "horizon": h,
                    "forward_return": bar[0, f"forward_return_{h}"],
                    "hit_up": bar[0, f"hit_up_{h}"],
                    "hit_down": bar[0, f"hit_down_{h}"],
                    "max_favorable": bar[0, f"max_favorable_{h}"],
                    "max_adverse": bar[0, f"max_adverse_{h}"],
                    "realized_vol_future": bar[0, f"realized_vol_future_{h}"],
                }
            )
    return pl.DataFrame(rows)
