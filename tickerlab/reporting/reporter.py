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


def create_quote_table(q: dict) -> Table:
    sym = q["symbol"]
    curr = q.get("currency", "USD")
    price = q.get("price")
    chg = q.get("change")
    pct = q.get("change_pct")

    color = "green" if chg and chg >= 0 else "red"
    sign = "+" if chg and chg >= 0 else ""

    table = Table(title=f"TickerLab Live Quote: [bold]{sym}[/bold]", show_header=True, header_style="bold cyan")
    table.add_column("Campo", style="dim")
    table.add_column("Valor", justify="right")

    table.add_row("Precio Actual", f"[{color}][bold]{price:,.2f} {curr}[/bold][/{color}]" if price is not None else "N/A")
    if chg is not None and pct is not None:
        table.add_row("Variación", f"[{color}]{sign}{chg:,.2f} ({sign}{pct:.2f}%)[/{color}]")
    table.add_row("Cierre Anterior", f"{q['prev_close']:,.2f} {curr}" if q.get("prev_close") is not None else "N/A")
    table.add_row("Apertura", f"{q['open']:,.2f} {curr}" if q.get("open") is not None else "N/A")
    if q.get("day_low") is not None and q.get("day_high") is not None:
        table.add_row("Rango del Día", f"{q['day_low']:,.2f} - {q['day_high']:,.2f} {curr}")
    if q.get("volume") is not None:
        table.add_row("Volumen", f"{q['volume']:,}")
    table.add_row("Zona Horaria", str(q.get("timezone", "N/A")))
    table.add_row("Hora Consulta", q.get("timestamp", "")[:19].replace("T", " "))
    return table


def print_quote(q: dict) -> None:
    Console().print(create_quote_table(q))


def export(df: pl.DataFrame, output_path: Path, fmt: str) -> Path:
    return save_frame(df, output_path, export=fmt)
