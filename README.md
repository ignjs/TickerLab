# TickerLab

TickerLab es una herramienta CLI para análisis cuantitativo de patrones en tickers bursátiles.

## Estado V1 (MVP)

Incluye un pipeline E2E mínimo:

1. Ingesta (`csv` o `synthetic`) y normalización OHLCV.
2. Cálculo de features cuantitativos vectorizados.
3. Detección de pivots locales.
4. Escaneo de patrones estructurales (double top / double bottom).
5. Etiquetado futuro multi-horizonte (forward returns, hit_up/down, excursions).
6. Validación walk-forward (`rolling` y `expanding`) con purga temporal.
7. Métricas out-of-sample y exportación CSV/JSON/Parquet.

## Instalación

```bash
python -m pip install -e .[dev]
```

## Comandos CLI

```bash
tickerlab ingest --symbol AAPL --timeframe 1d --source synthetic
tickerlab features build --symbol AAPL --timeframe 1d
tickerlab patterns scan --symbol AAPL --engine structural
tickerlab labels build --symbol AAPL --horizons 1,3,5,10,20,60
tickerlab validate walkforward --symbol AAPL --model logistic --mode rolling
tickerlab score now --symbol AAPL
tickerlab report edge --symbol AAPL --format table
```

## Exportación

Los comandos de pipeline soportan `--export parquet|csv|json` y guardan resultados en:

- `data/bars/...`
- `data/features/...`
- `data/pivots/...`
- `data/events/...`
- `data/labels_bar/...`
- `data/labels_event/...`
- `data/validation_folds/...`
- `data/validation_summary/...`

## Testing

```bash
pytest
```

Incluye:

- Unit tests (`tests/unit`)
- Integration test E2E (`tests/integration`)
- Property test de no-leakage temporal (`tests/property`)
- Benchmark básico (`benchmarks/test_benchmark_pipeline.py`)
