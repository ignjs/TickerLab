from __future__ import annotations

from pathlib import Path

import polars as pl
from rich.console import Console
from rich.table import Table

from tickerlab.storage.io import save_frame


def print_metrics(metrics: dict[str, float]) -> None:
    table = Table(title="TickerLab OOS Metrics")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    for k, v in metrics.items():
        table.add_row(k, f"{v:.6f}" if isinstance(v, float) else str(v))
    Console().print(table)


def export(df: pl.DataFrame, output_path: Path, fmt: str) -> Path:
    return save_frame(df, output_path, export=fmt)
