from __future__ import annotations

from pathlib import Path

import polars as pl
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

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


def print_accessible_report(
    symbol: str,
    quote: dict | None,
    summary: dict[str, float] | None,
    score_now: float | None = None,
    events_count: int = 0,
    explain: bool = False,
    message: str | None = None,
    note: str | None = None,
) -> None:
    console = Console()

    if note:
        console.print(f"[bold cyan]ℹ️  {note}[/bold cyan]\n")

    # Header Panel
    if quote:
        price = quote.get("price", 0.0)
        curr = quote.get("currency", "USD")
        chg = quote.get("change")
        pct = quote.get("change_pct")
        if chg is not None:
            col = "green" if chg >= 0 else "red"
            sign = "+" if chg >= 0 else ""
            var_str = f"[{col}]{sign}{chg:,.2f} ({sign}{pct:.2f}%)[/{col}]"
        else:
            var_str = "N/A"
        header_text = Text.from_markup(
            f"[bold white]📊 REPORTE DE ANÁLISIS: [cyan]{symbol}[/cyan][/bold white]\n"
            f"Precio en Vivo: [bold]{price:,.2f} {curr}[/bold]  │  "
            f"Variación: {var_str}"
        )
    else:
        header_text = Text.from_markup(f"[bold white]📊 REPORTE DE ANÁLISIS: [cyan]{symbol}[/cyan][/bold white]")

    console.print(Panel(header_text, style="bold blue", expand=False))

    if message:
        console.print(f"\n[yellow]⚠️  {message}[/yellow]\n")
        return

    if not summary:
        console.print("[yellow]No se pudieron calcular métricas de validación para este activo.[/yellow]")
        return

    # 1. Historical Pattern Reliability
    hit_rate = summary.get("hit_rate", 0.0)
    pf = summary.get("profit_factor", 0.0)
    sharpe = summary.get("sharpe", 0.0)
    dd = summary.get("max_drawdown", 0.0)

    if hit_rate >= 0.70:
        hr_eval = "[bold green]Excelente[/bold green] (más de 7 de cada 10 señales subieron)"
    elif hit_rate >= 0.55:
        hr_eval = "[green]Favorable[/green] (ventaja estadística positiva)"
    else:
        hr_eval = "[yellow]Moderada / Cercana al azar[/yellow]"

    if pf >= 3.0:
        pf_eval = f"[bold green]{pf:.2f}x[/bold green] (Gana {pf:.2f} veces lo que arriesga)"
    elif pf >= 1.5:
        pf_eval = f"[green]{pf:.2f}x[/green] (Rentable)"
    else:
        pf_eval = f"[yellow]{pf:.2f}x[/yellow] (Margen estrecho)"

    if sharpe >= 3.0:
        sharpe_eval = "[bold green]Sobresaliente[/bold green] (alto retorno ajustado por riesgo)"
    elif sharpe >= 1.5:
        sharpe_eval = "[green]Bueno[/green]"
    else:
        sharpe_eval = "[yellow]Bajo o Volátil[/yellow]"

    hist_table = Table(
        title="[bold cyan][1] Fiabilidad Histórica del Patrón (Double Bottom / Top)[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )
    hist_table.add_column("Métrica Clave", style="dim")
    hist_table.add_column("Resultado", justify="right")
    hist_table.add_column("Interpretación para Inversores")

    filled = max(0, min(10, int(round(hit_rate * 10))))
    bar = f"[green][{'█' * filled}{'░' * (10 - filled)}][/green]"
    hist_table.add_row("Tasa de Acierto", f"{hit_rate * 100:.1f}% {bar}", hr_eval)
    hist_table.add_row("Relación Ganancia / Pérdida", f"{pf:.2f}x", pf_eval)
    hist_table.add_row("Calidad del Modelo (Sharpe)", f"{sharpe:.2f}", sharpe_eval)
    hist_table.add_row("Caída Temporal Máxima", f"{dd * 100:.2f}%", f"[yellow]{abs(dd)*100:.1f}% de pérdida temporal máxima[/yellow]")
    hist_table.add_row("Formaciones Evaluadas", str(events_count), "Figuras técnicas validadas out-of-sample")

    console.print(hist_table)

    # 2. Real-Time Diagnosis
    if score_now is not None:
        prob_pct = score_now * 100
        if score_now >= 0.65:
            sem = "🟢 [bold green]SEÑAL ALCISTA ACTIVA[/bold green]"
            verdict = "Se detectó una formación técnica con alta probabilidad estadística de subida en el corto plazo."
        elif score_now >= 0.45:
            sem = "🟡 [bold yellow]ZONA DE OBSERVACIÓN / NEUTRAL[/bold yellow]"
            verdict = "El activo está en fase de consolidación. No hay una ventaja clara hoy; se sugiere esperar confirmación."
        else:
            sem = "⚪ [bold white]SIN ACTIVACIÓN / ESPERAR[/bold white]"
            verdict = "Aunque el patrón tiene buen historial en este activo, HOY no hay una figura alcista confirmada. Se sugiere esperar."

        diag_table = Table(title="[bold cyan][2] Diagnóstico en Tiempo Real (¿Qué hacer hoy?)[/bold cyan]", show_header=False)
        diag_table.add_column("Campo", style="dim")
        diag_table.add_column("Detalle")
        diag_table.add_row("Semáforo Actual", sem)
        diag_table.add_row("Probabilidad de Subida (5d)", f"[bold]{prob_pct:.1f}%[/bold]")
        diag_table.add_row("Veredicto Sencillo", verdict)
        console.print(diag_table)

    # 3. Explain Glossary (if explain=True)
    if explain:
        exp_table = Table(
            title="[bold yellow]📖 Glosario y Conceptos para Principiantes[/bold yellow]",
            show_header=True,
            header_style="bold yellow",
        )
        exp_table.add_column("Concepto", style="bold")
        exp_table.add_column("¿Qué significa en lenguaje sencillo?")
        exp_table.add_row("Tasa de Acierto (Hit Rate)", "Porcentaje de veces que el precio subió tras completarse la figura técnica.")
        exp_table.add_row(
            "Relación Ganancia/Pérdida (Profit Factor)",
            "Mide cuánto dinero ganó la estrategia por cada peso/dólar que perdió en operaciones fallidas. Mayor a 1.5 es bueno; mayor a 3.0 es excelente.",
        )
        exp_table.add_row("Calidad / Sharpe Ratio", "Mide cuánto retorno genera el activo por cada unidad de volatilidad o riesgo asumido.")
        exp_table.add_row("Caída Máxima (Drawdown)", "La mayor pérdida temporal que experimentó la posición antes de recuperarse.")
        exp_table.add_row("Double Bottom (Doble Suelo)", "Figura técnica en forma de 'W' que indica que el precio tocó un piso dos veces y tiende a rebotar al alza.")
        exp_table.add_row("Double Top (Doble Techo)", "Figura técnica en forma de 'M' que indica que el precio no pudo superar un techo y tiende a corregir.")
        exp_table.add_row("Validación Walk-Forward", "Simulación rigurosa que prueba el modelo exclusivamente en datos futuros a la fecha de entrenamiento, evitando sesgos.")
        console.print(exp_table)
