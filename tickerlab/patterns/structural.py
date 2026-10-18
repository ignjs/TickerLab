from __future__ import annotations

import polars as pl


def scan_structural(pivots: pl.DataFrame, tolerance: float = 0.01) -> pl.DataFrame:
    if pivots.height < 3:
        return pl.DataFrame(
            {
                "event_id": [],
                "ts_start": [],
                "ts_end": [],
                "symbol": [],
                "pattern_type": [],
                "confidence": [],
                "params": [],
                "pivot_count": [],
                "regime_id": [],
                "source_engine": [],
            }
        )

    rows = []
    p = pivots.sort("ts")
    for i in range(2, p.height):
        a, b, c = p.row(i - 2, named=True), p.row(i - 1, named=True), p.row(i, named=True)
        if a["pivot_type"] == "high" and b["pivot_type"] == "low" and c["pivot_type"] == "high":
            rel = abs(float(a["price"]) - float(c["price"])) / max(float(a["price"]), 1e-8)
            if rel <= tolerance:
                rows.append(
                    {
                        "event_id": f"dt_{i}",
                        "ts_start": a["ts"],
                        "ts_end": c["ts"],
                        "symbol": a["symbol"],
                        "pattern_type": "double_top",
                        "confidence": float(max(0.0, 1.0 - rel / max(tolerance, 1e-8))),
                        "params": f"tol={tolerance}",
                        "pivot_count": 3,
                        "regime_id": "unknown",
                        "source_engine": "structural",
                    }
                )
        if a["pivot_type"] == "low" and b["pivot_type"] == "high" and c["pivot_type"] == "low":
            rel = abs(float(a["price"]) - float(c["price"])) / max(float(a["price"]), 1e-8)
            if rel <= tolerance:
                rows.append(
                    {
                        "event_id": f"db_{i}",
                        "ts_start": a["ts"],
                        "ts_end": c["ts"],
                        "symbol": a["symbol"],
                        "pattern_type": "double_bottom",
                        "confidence": float(max(0.0, 1.0 - rel / max(tolerance, 1e-8))),
                        "params": f"tol={tolerance}",
                        "pivot_count": 3,
                        "regime_id": "unknown",
                        "source_engine": "structural",
                    }
                )

    if not rows:
        return scan_structural(pl.DataFrame(), tolerance)
    return pl.DataFrame(rows)
