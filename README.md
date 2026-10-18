# TickerLab

TickerLab es una herramienta CLI orientada al análisis cuantitativo, detección de patrones técnicos y validación estadística out-of-sample en series temporales financieras (tickers bursátiles).

El proyecto implementa un pipeline End-to-End (E2E) robusto y vectorizado que minimiza el sesgo de anticipación (*lookahead bias*) y la fuga temporal (*data leakage*).

---

## Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Pipeline Cuantitativo (Paso a Paso)](#pipeline-cuantitativo-paso-a-paso)
- [Comandos CLI y Ejemplos](#comandos-cli-y-ejemplos)
- [Formatos de Exportación](#formatos-de-exportación)
- [Ingesta desde Archivos CSV](#ingesta-desde-archivos-csv)
- [Testing y Benchmarks](#testing-y-benchmarks)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Solución de Problemas (Troubleshooting)](#solución-de-problemas-troubleshooting)

---

## Requisitos Previos

- **Python**: `>= 3.11` (probado en Python 3.12).
- **Sistema Operativo**: Linux, macOS o Windows (WSL recomendado).

---

## Instalación

### 1. Clonar el repositorio y crear el entorno virtual

En sistemas Linux modernos (Debian/Ubuntu con PEP 668), es necesario utilizar un entorno virtual para evitar conflictos con el sistema:

```bash
# Crear el entorno virtual
python3 -m venv .venv

# Activar el entorno virtual
source .venv/bin/activate
# En Windows (cmd/powershell): .venv\Scripts\activate
```

### 2. Instalar el paquete en modo editable

Con el entorno virtual activado:

```bash
pip install -e .[dev]
```

### 3. Compatibilidad con procesadores sin AVX2 (Opcional)

Si ejecutas el proyecto en procesadores antiguos (ej. Intel Ivy Bridge / Sandy Bridge de 2da o 3ra generación) o máquinas virtuales sin soporte para instrucciones vectoriales AVX2, instala el paquete de compatibilidad de Polars para evitar errores de tipo `Illegal instruction`:

```bash
pip install "polars[rtcompat]"
```

---

## Pipeline Cuantitativo (Paso a Paso)

El análisis en TickerLab sigue una secuencia modular y determinista. Cada comando almacena sus resultados en disco (`data/`), sirviendo de entrada para la siguiente etapa:

```text
[1. Ingesta]           --> data/bars/             (Velas OHLCV normalizadas)
     │
     ▼
[2. Features]          --> data/features/         (Indicadores y retornos vectorizados)
     │
     ▼
[3. Patrones & Pivots] --> data/pivots/, events/  (Detección de extremos y formaciones)
     │
     ▼
[4. Etiquetas]         --> data/labels_*          (Retornos forward multi-horizonte)
     │
     ▼
[5. Validación]        --> data/validation_*      (Walk-forward con purga temporal)
     │
     ▼
[6. Reporte & Score]   --> Consola / Exportación  (Métricas OOS e inferencia actual)
```

> **Importante**: Los comandos dependen de los datos generados por el paso previo. Por ejemplo, no es posible generar un reporte (`report edge`) de un ticker si antes no se ha corrido su validación (`validate walkforward`).

---

## Comandos CLI y Ejemplos

A continuación se muestra un ciclo de trabajo completo para un símbolo (ej. `AAPL` o `IAM.SN`):

### Paso 1: Ingesta de datos
Genera barras OHLCV sintéticas o carga datos históricos:
```bash
# Ingesta desde Yahoo Finance (Datos reales de Nueva York y Bolsa de Santiago):
# Mercado de EE.UU. (NYSE / NASDAQ):
tickerlab ingest --symbol IONQ --timeframe 1d --source yahoo
tickerlab ingest --symbol AAPL --timeframe 1d --source yahoo

# Bolsa de Santiago (Chile) - usar sufijo .SN:
tickerlab ingest --symbol IAM.SN --timeframe 1d --source yahoo
tickerlab ingest --symbol SQM-B.SN --timeframe 1d --source yahoo
tickerlab ingest --symbol CHILE.SN --timeframe 1d --source yahoo

# Ingesta sintética (genera automáticamente una serie reproducible según el símbolo):
tickerlab ingest --symbol AAPL --timeframe 1d --source synthetic

# Opcional: Especificar una semilla manual en sintético
tickerlab ingest --symbol AAPL --timeframe 1d --source synthetic --seed 42
```

### Paso 2: Construcción de features
Calcula retornos forward/backward, medias móviles, volatilidad realizada, RSI y z-scores:
```bash
tickerlab features build --symbol AAPL --timeframe 1d
```

### Paso 3: Detección de pivots y escaneo de patrones
Detecta máximos y mínimos locales y busca formaciones estructurales (ej. Double Top / Double Bottom):
```bash
tickerlab patterns scan --symbol AAPL --engine structural
```

### Paso 4: Construcción de etiquetas futuras
Genera etiquetas multi-horizonte (1, 3, 5, 10, 20 y 60 períodos) para barras y eventos:
```bash
tickerlab labels build --symbol AAPL --horizons 1,3,5,10,20,60
```

### Paso 5: Validación Walk-Forward
Entrena y valida el modelo predictivo (regresión logística) mediante ventanas móviles (`rolling`) o expansivas (`expanding`) con purga temporal out-of-sample:
```bash
tickerlab validate walkforward --symbol AAPL --model logistic --mode rolling
```

### Paso 6: Scoring actual (Inferencia)
Calcula la probabilidad predictiva para la barra más reciente del activo:
```bash
tickerlab score now --symbol AAPL
```

### Paso 7: Reporte de métricas Out-Of-Sample (OOS)
Muestra la tabla de rendimiento fuera de muestra (Hit Rate, Profit Factor, Sharpe, Max Drawdown, AUC, Brier Score, etc.):
```bash
tickerlab report edge --symbol AAPL --format table
```

### Paso 8: Consulta de Cotización en Tiempo Real (`quote`)
Permite inspeccionar el precio actual, variación diaria (monto y %), rango del día, volumen y zona horaria para activos de EE.UU. o Chile:
```bash
# Consulta rápida (EE.UU. o Chile):
tickerlab quote IONQ
tickerlab quote IAM.SN

# O usando el flag --symbol:
tickerlab quote --symbol SQM-B.SN

# Monitoreo continuo en vivo (se refresca automáticamente cada N segundos):
tickerlab quote IONQ --watch --interval 5
```

---

## Formatos de Exportación

Por defecto, los datos intermedios y finales se guardan en formato binario **Parquet** (`.parquet`) por motivos de rendimiento y compresión. 

Si deseas exportar los resultados para inspeccionarlos en hojas de cálculo o editores de texto, puedes utilizar el parámetro `--export`:

```bash
# Exportar el reporte en CSV
tickerlab report edge --symbol AAPL --format csv

# Exportar en JSON
tickerlab report edge --symbol AAPL --format json
```

Los artefactos se organizan por particiones bajo `data/`:
- `data/bars/symbol={SYM}/timeframe={TF}/`
- `data/features/symbol={SYM}/timeframe={TF}/`
- `data/pivots/symbol={SYM}/timeframe={TF}/`
- `data/events/symbol={SYM}/timeframe={TF}/`
- `data/labels_bar/symbol={SYM}/timeframe={TF}/`
- `data/labels_event/symbol={SYM}/timeframe={TF}/`
- `data/validation_folds/symbol={SYM}/timeframe={TF}/`
- `data/validation_summary/symbol={SYM}/timeframe={TF}/`

---

## Ingesta desde Archivos CSV

Para analizar datos propios en formato CSV:

```bash
tickerlab ingest --symbol MI_TICKER --timeframe 1d --source csv --input-path ruta/al/archivo.csv
```

El archivo CSV debe contener como mínimo las siguientes columnas:
- `timestamp` (formato ISO-8601 o fecha estándar)
- `open`
- `high`
- `low`
- `close`
- `volume`

También puedes apoyarte en un archivo de configuración YAML como el provisto en [`configs/default.yaml`](configs/default.yaml):

```bash
tickerlab ingest --config configs/default.yaml
```

---

## Testing y Benchmarks

El repositorio incluye un conjunto integral de pruebas para asegurar la exactitud de los algoritmos y la ausencia de *data leakage*:

```bash
# Ejecutar suite básica (unit, integration y property tests)
pytest

# Ejecutar con detalles y salida legible
pytest -v

# Ejecutar suite completa incluyendo benchmarks de rendimiento
pytest tests benchmarks
```

Tipos de pruebas incluidas:
- **`tests/unit/`**: Pruebas unitarias de cálculos de features, normalización y detección de pivots.
- **`tests/integration/`**: Flujo completo del pipeline E2E.
- **`tests/property/`**: Pruebas basadas en propiedades (con Hypothesis) para certificar matemáticamente que no exista fuga de información temporal entre train y test.
- **`benchmarks/`**: Medición de latencia y rendimiento de procesamiento.

---

## Estructura del Proyecto

```text
TickerLab/
├── benchmarks/              # Pruebas de rendimiento del pipeline
├── configs/                 # Configuraciones por defecto (default.yaml)
├── data/                    # Almacenamiento local de artefactos generados (ignorado en git)
├── tests/                   # Suites de tests
│   ├── integration/         # Tests de pipeline completo
│   ├── property/            # Property tests (no-leakage) con Hypothesis
│   └── unit/                # Tests de componentes individuales
├── tickerlab/               # Código fuente del paquete
│   ├── cli/                 # Definición de comandos CLI (Typer & Rich)
│   ├── config/              # Modelos de configuración Pydantic
│   ├── features/            # Motores de extracción de features cuantitativos
│   ├── ingest/              # Ingesta y normalización OHLCV (CSV / Sintético)
│   ├── labels/              # Etiquetado multi-horizonte
│   ├── models/              # Modelos estadísticos y baseline ML
│   ├── patterns/            # Escaneo de patrones estructurales
│   ├── pivots/              # Algoritmos de detección de pivots
│   ├── reporting/           # Formateo de tablas y reportes de métricas
│   ├── stats/               # Cálculo de métricas estadísticas y financieras
│   ├── storage/             # Funciones I/O (Parquet/CSV/JSON)
│   ├── utils/               # Utilidades de dataset y transformación
│   └── validation/          # Validación walk-forward y purga temporal
├── pyproject.toml           # Dependencias y configuración de empaquetado
└── README.md                # Documentación principal
```

---

## Solución de Problemas (Troubleshooting)

### 1. `error: externally-managed-environment`
- **Causa**: Intentar instalar dependencias con `pip` en el entorno global del sistema en Linux (PEP 668).
- **Solución**: Asegúrate de activar el entorno virtual antes de instalar paquetes (`source .venv/bin/activate`).

### 2. `Fatal Python error: Illegal instruction`
- **Causa**: Polars intentando ejecutar instrucciones de CPU modernas (AVX2) en un procesador que no las soporta.
- **Solución**: Instala la versión compatible ejecutando `pip install "polars[rtcompat]"`.

### 3. `FileNotFoundError: No such file or directory: data/validation_summary/...`
- **Causa**: Intentar ejecutar `tickerlab report edge` antes de haber generado la validación del activo.
- **Solución**: Sigue el orden del pipeline y ejecuta previamente `tickerlab features build`, `tickerlab patterns scan`, `tickerlab labels build` y `tickerlab validate walkforward` para ese símbolo.

### 4. Visualización de archivos `.parquet`
- **Causa**: Los archivos `.parquet` son binarios y no pueden leerse en un editor de texto convencional.
- **Solución**: Usa una extensión de visor de Parquet en el IDE, o exporta el reporte/datos usando `--format csv` / `--export csv`.
