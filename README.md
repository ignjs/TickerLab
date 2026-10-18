# TickerLab 📈

**Análisis cuantitativo y detección de patrones técnicos con rigor estadístico.**

TickerLab es una herramienta CLI diseñada para transformar datos financieros brutos en señales predictivas validadas. Implementa un pipeline End-to-End (E2E) vectorizado que elimina el sesgo de anticipación (*lookahead bias*) y garantiza que los resultados sean estadísticamente significativos mediante validación *walk-forward*.

### 🚀 Quick Start: Del Dato al Reporte en un Segundo

La forma más rápida de experimentar la potencia de TickerLab es el comando `analyze`. Este automatiza todo el flujo (Ingesta $\rightarrow$ Features $\rightarrow$ Patrones $\rightarrow$ Validación $\rightarrow$ Reporte) en una sola ejecución:

```bash
# Análisis completo de un activo (ej. Apple)
tickerlab analyze AAPL

# Análisis con glosario explicativo para principiantes
tickerlab analyze AAPL --explain

# Análisis offline usando datos sintéticos reproducibles
tickerlab analyze AAPL --source synthetic
```

---

### ⚙️ El Core Tecnológico

TickerLab no es solo un conjunto de scripts, es un motor de análisis optimizado:

*   **Velocidad Extrema**: Construido sobre **Polars** y **Numba** para procesamiento vectorizado y compilación JIT.
*   **Rigor Temporal**: Implementa **Walk-Forward Validation** con purga temporal para evitar la fuga de datos (*data leakage*).
*   **Persistencia Eficiente**: Almacenamiento en formato **Parquet** para alta compresión y lectura rápida.
*   **Certificación Matemática**: Pruebas basadas en propiedades con **Hypothesis** para validar invariantes temporales.

---

### 🛠️ Pipeline de Análisis

El sistema procesa la información en un flujo modular y determinista:

**Datos Brutos** $\rightarrow$ `Ingest` $\rightarrow$ `Features` $\rightarrow$ `Patterns` $\rightarrow$ `Labels` $\rightarrow$ `Walk-Forward` $\rightarrow$ **Edge Score**

Cada etapa persiste sus resultados en `data/`, permitiendo el control granular de cada fase del proceso.

---

### 📖 Guía de Referencia

#### 1. Instalación Rápida
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```
*(Si tienes un procesador antiguo sin AVX2, ejecuta: `pip install "polars[rtcompat]"`)*

#### 2. Control Avanzado (Flujo Detallado)
Para quienes necesitan controlar cada parámetro, el pipeline se puede ejecutar paso a paso:

| Fase | Comando | Propósito |
| :--- | :--- | :--- |
| **1. Ingesta** | `tickerlab ingest` | Carga datos de Yahoo Finance, CSV o Sintéticos |
| **2. Features** | `tickerlab features build` | Calcula indicadores técnicos y Z-Scores |
| **3. Patrones** | `tickerlab patterns scan` | Detecta Pivots y estructuras (Double Top/Bottom) |
| **4. Etiquetas** | `tickerlab labels build` | Genera retornos forward multi-horizonte |
| **5. Validación** | `tickerlab validate walkforward` | Entrena y valida el modelo OOS |
| **6. Inferencia** | `tickerlab score now` | Probabilidad predictiva de la barra actual |
| **7. Reporte** | `tickerlab report edge` | Métricas de rendimiento (Hit Rate, Sharpe, AUC) |

#### 3. Utilidades Adicionales
- **Cotizaciones en vivo**: `tickerlab quote SYMBOL`
- **Exportación**: Usa `--format csv` o `--format json` en los reportes para extraer datos.

---

### 🧪 Calidad y Validación

El proyecto incluye una suite de tests exhaustiva para garantizar la fiabilidad de las señales:
- **Unit Tests**: Validación de cálculos matemáticos.
- **Integration Tests**: Verificación del flujo E2E.
- **Property Tests**: Certificación de no-fuga de datos (No-Leakage).
- **Benchmarks**: Medición de latencia de procesamiento.

Ejecutar todo con: `pytest`

---

### 📂 Estructura Simplificada
- `tickerlab/`: Código fuente (CLI, Ingest, Features, Validation).
- `data/`: Artefactos generados (Parquet).
- `tests/`: Suites de validación y benchmarks.
- `configs/`: Parámetros por defecto.

---

### 🆘 Troubleshooting
- **`externally-managed-environment`**: Activa tu entorno virtual (`source .venv/bin/activate`).
- **`Illegal instruction`**: Instala `polars[rtcompat]`.
- **`FileNotFoundError`**: Asegúrate de seguir el orden del pipeline o usa `tickerlab analyze`.


---

## Requisitos Previos

- **Python**: `>= 3.11` (probado en Python 3.12).
- **Sistema Operativo**: Linux, macOS o Windows (WSL recomendado).
- **Stack Tecnológico Clave**:
  - **Polars**: Para procesamiento de datos vectorizado y eficiente en memoria.
  - **Numba**: Para aceleración de funciones críticas mediante compilación JIT.
  - **PyArrow**: Para persistencia de datos en formato Parquet.
  - **Hypothesis**: Para validación de invariantes temporales (evitar data leakage).

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

### 🚀 Análisis Rápido (One-Click)

Si no deseas ejecutar cada paso del pipeline manualmente, puedes utilizar el comando `analyze`. Este automatiza la ingesta, el cálculo de indicadores, la detección de patrones y la validación estadística en un solo paso, entregando un reporte visual completo.

```bash
# Análisis completo de un activo (ej. Apple)
tickerlab analyze AAPL

# Análisis con explicación detallada para principiantes
tickerlab analyze AAPL --explain

# Análisis utilizando datos sintéticos (sin conexión a internet)
tickerlab analyze AAPL --source synthetic
```

---

### Flujo de Trabajo Detallado (Paso a Paso)

A continuación se muestra el ciclo de trabajo completo para un símbolo (ej. `AAPL` o `IAM.SN`) si deseas controlar cada etapa del proceso:

### Paso 1: Ingesta de datos
Genera barras OHLCV sintéticas, carga datos históricos o importa archivos propios. El sistema normaliza automáticamente los nombres de las columnas (ej. `adj close` o `timestamp` se convierten a estándares internos).

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

# Ingesta sintética (genera automáticamente una serie reproducible basada en el hash del símbolo):
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
