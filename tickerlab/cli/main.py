from __future__ import annotations

from pathlib import Path

import polars as pl
import typer

from tickerlab.config.models import load_config
from tickerlab.features.builder import build_features
from tickerlab.ingest.service import load_from_csv, load_synthetic
from tickerlab.labels.builder import build_bar_labels, build_event_labels
from tickerlab.models.baseline import fit_logistic
from tickerlab.patterns.structural import scan_structural
from tickerlab.pivots.detector import detect_pivots
from tickerlab.reporting.reporter import print_metrics
from tickerlab.stats.metrics import compute_signal_metrics, stability_score
from tickerlab.storage.io import dataset_path, load_frame, save_frame
from tickerlab.utils.dataset import as_xy, event_dataset
from tickerlab.validation.walkforward import walk_forward_indices

app = typer.Typer(help="TickerLab CLI")
features_app = typer.Typer(help="Feature commands")
patterns_app = typer.Typer(help="Pattern commands")
labels_app = typer.Typer(help="Label commands")
validate_app = typer.Typer(help="Validation commands")
score_app = typer.Typer(help="Scoring commands")
report_app = typer.Typer(help="Reporting commands")

app.add_typer(features_app, name="features")
app.add_typer(patterns_app, name="patterns")
app.add_typer(labels_app, name="labels")
app.add_typer(validate_app, name="validate")
app.add_typer(score_app, name="score")
app.add_typer(report_app, name="report")


def _save(cache_dir: Path, name: str, symbol: str, timeframe: str, df: pl.DataFrame, export: str = "parquet") -> Path:
    path = dataset_path(cache_dir, name, symbol, timeframe, export)
    save_frame(df, path, export=export)
    return path


@app.command()
def ingest(
    symbol: str = "AAPL",
    timeframe: str = "1d",
    source: str = "synthetic",
    input_path: str | None = None,
    config: str | None = None,
    cache_dir: str = "data",
    export: str = "parquet",
):
    cfg = load_config(config)
    source = source or cfg.ingest.source
    input_path = input_path or cfg.ingest.input_path
    if source == "csv":
        if not input_path:
            raise typer.BadParameter("--input-path es requerido cuando source=csv")
        bars = load_from_csv(input_path, symbol=symbol, timeframe=timeframe)
    else:
        bars = load_synthetic(symbol=symbol, timeframe=timeframe)
    path = _save(Path(cache_dir), "bars", symbol, timeframe, bars, export=export)
    typer.echo(f"ingested={bars.height} path={path}")


@features_app.command("build")
def features_build(symbol: str = "AAPL", timeframe: str = "1d", cache_dir: str = "data", export: str = "parquet"):
    bars = load_frame(dataset_path(Path(cache_dir), "bars", symbol, timeframe))
    feats = build_features(bars)
    path = _save(Path(cache_dir), "features", symbol, timeframe, feats, export=export)
    typer.echo(f"features={feats.height} path={path}")


@patterns_app.command("scan")
def patterns_scan(symbol: str = "AAPL", timeframe: str = "1d", engine: str = "structural", cache_dir: str = "data", export: str = "parquet"):
    if engine != "structural":
        raise typer.BadParameter("Engine soportado en V1 mínima: structural")
    bars = load_frame(dataset_path(Path(cache_dir), "bars", symbol, timeframe))
    piv = detect_pivots(bars, window=3)
    events = scan_structural(piv, tolerance=0.01)
    _save(Path(cache_dir), "pivots", symbol, timeframe, piv, export=export)
    path = _save(Path(cache_dir), "events", symbol, timeframe, events, export=export)
    typer.echo(f"events={events.height} path={path}")


@labels_app.command("build")
def labels_build(symbol: str = "AAPL", timeframe: str = "1d", horizons: str = "1,3,5,10,20,60", cache_dir: str = "data", export: str = "parquet"):
    hs = [int(x.strip()) for x in horizons.split(",") if x.strip()]
    bars = load_frame(dataset_path(Path(cache_dir), "bars", symbol, timeframe))
    events = load_frame(dataset_path(Path(cache_dir), "events", symbol, timeframe))
    lab_bar = build_bar_labels(bars, horizons=hs)
    lab_event = build_event_labels(bars, events, horizons=hs)
    path_b = _save(Path(cache_dir), "labels_bar", symbol, timeframe, lab_bar, export=export)
    path_e = _save(Path(cache_dir), "labels_event", symbol, timeframe, lab_event, export=export)
    typer.echo(f"labels_bar={lab_bar.height} {path_b}")
    typer.echo(f"labels_event={lab_event.height} {path_e}")


@validate_app.command("walkforward")
def validate_walkforward(
    symbol: str = "AAPL",
    timeframe: str = "1d",
    model: str = "logistic",
    mode: str = "rolling",
    horizon: int = 5,
    cache_dir: str = "data",
    export: str = "parquet",
):
    if model != "logistic":
        raise typer.BadParameter("Modelo soportado en V1 mínima: logistic")
    if mode not in {"rolling", "expanding"}:
        raise typer.BadParameter("mode debe ser rolling o expanding")

    feats = load_frame(dataset_path(Path(cache_dir), "features", symbol, timeframe))
    events = load_frame(dataset_path(Path(cache_dir), "events", symbol, timeframe))
    labels_event = load_frame(dataset_path(Path(cache_dir), "labels_event", symbol, timeframe))
    ds = event_dataset(feats, events, labels_event, horizon=horizon)
    X, y, fr, sub = as_xy(ds)
    if len(y) < 20:
        raise typer.BadParameter("Muy pocos eventos válidos para walk-forward")

    folds = list(walk_forward_indices(len(y), mode=mode, train_size=50, test_size=20, n_splits=5, purge=1))
    fold_rows = []
    aucs = []
    for i, fold in enumerate(folds):
        Xtr, ytr = X[fold.train_idx], y[fold.train_idx]
        Xte, yte = X[fold.test_idx], y[fold.test_idx]
        frte = fr[fold.test_idx]
        clf = fit_logistic(Xtr, ytr)
        prob = clf.predict_proba(Xte)[:, 1]
        m = compute_signal_metrics(yte, prob, frte)
        aucs.append(m["auc"])
        fold_rows.append({"fold": i, **m})

    summary = compute_signal_metrics(y, fit_logistic(X, y).predict_proba(X)[:, 1], fr)
    summary["stability_score"] = stability_score([x for x in aucs if x == x])
    folds_df = pl.DataFrame(fold_rows)
    summary_df = pl.DataFrame([summary])
    _save(Path(cache_dir), "validation_folds", symbol, timeframe, folds_df, export=export)
    out = _save(Path(cache_dir), "validation_summary", symbol, timeframe, summary_df, export=export)
    print_metrics(summary)
    typer.echo(f"validation={out} rows={sub.height}")


@score_app.command("now")
def score_now(symbol: str = "AAPL", timeframe: str = "1d", horizon: int = 5, cache_dir: str = "data"):
    feats = load_frame(dataset_path(Path(cache_dir), "features", symbol, timeframe))
    events = load_frame(dataset_path(Path(cache_dir), "events", symbol, timeframe))
    labels_event = load_frame(dataset_path(Path(cache_dir), "labels_event", symbol, timeframe))
    ds = event_dataset(feats, events, labels_event, horizon=horizon)
    X, y, _, sub = as_xy(ds)
    model = fit_logistic(X, y)
    latest = sub.select([c for c in sub.columns if c in ["ret_1", "ret_5", "ema_ratio", "range_pct", "zscore_20", "vol_ratio_20", "rsi_14", "drawdown_20", "realized_vol_20"]]).tail(1).to_numpy()
    p = float(model.predict_proba(latest)[:, 1][0])
    typer.echo(f"score_now={p:.6f}")


@report_app.command("edge")
def report_edge(symbol: str = "AAPL", timeframe: str = "1d", cache_dir: str = "data", format: str = "table"):
    summary = load_frame(dataset_path(Path(cache_dir), "validation_summary", symbol, timeframe))
    if format == "table":
        print_metrics(summary.row(0, named=True))
    elif format in {"csv", "json", "parquet"}:
        out = dataset_path(Path(cache_dir), "report_edge", symbol, timeframe, export=format)
        save_frame(summary, out, export=format)
        typer.echo(f"exported={out}")
    else:
        raise typer.BadParameter("format debe ser table/csv/json/parquet")
