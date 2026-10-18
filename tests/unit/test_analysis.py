from unittest.mock import MagicMock, patch
from typer.testing import CliRunner

from tickerlab.analysis.engine import (
    analyze_ticker,
    fuzzy_suggest_symbol,
    normalize_symbol,
    validate_yahoo_symbol,
    _levenshtein,
)
from tickerlab.cli.main import app


def test_normalize_symbol_chile():
    sym, note = normalize_symbol("IAM")
    assert sym == "IAM.SN"
    assert note is not None
    assert "Bolsa de Santiago" in note

    sym, note = normalize_symbol("chile")
    assert sym == "CHILE.SN"

    sym, note = normalize_symbol("AAPL")
    assert sym == "AAPL"
    assert note is None


def test_levenshtein_basic():
    """Verifica distancias Levenshtein esperadas."""
    assert _levenshtein("", "") == 0
    assert _levenshtein("abc", "abc") == 0
    assert _levenshtein("abc", "abd") == 1
    assert _levenshtein("kitten", "sitting") == 3
    assert _levenshtein("AAPL", "AAPL") == 0
    assert _levenshtein("APPL", "AAPL") == 1


def test_fuzzy_suggest_chile_typo():
    """Typo de símbolo chileno debe sugerir el ticker correcto con sufijo .SN."""
    # "FALABEL" → "FALABELLA" (dist=2)
    result = fuzzy_suggest_symbol("FALABEL")
    assert result == "FALABELLA.SN"

    # "CENCOSUT" → "CENCOSUD" (dist=1)
    result = fuzzy_suggest_symbol("CENCOSUT")
    assert result == "CENCOSUD.SN"


def test_fuzzy_suggest_us_typo():
    """Typo de símbolo US debe sugerir el ticker correcto."""
    # "APPL" → "AAPL" (dist=1)
    result = fuzzy_suggest_symbol("APPL")
    assert result == "AAPL"

    # "TSLS" → "TSLA" (dist=1)
    result = fuzzy_suggest_symbol("TSLS")
    assert result == "TSLA"


def test_fuzzy_suggest_no_match():
    """Símbolos muy lejanos no deben retornar sugerencias."""
    result = fuzzy_suggest_symbol("XYZQWERT")
    assert result is None


def test_fuzzy_suggest_exact_match():
    """Coincidencia exacta (dist=0) debe retornar el símbolo correcto."""
    result = fuzzy_suggest_symbol("AAPL")
    assert result == "AAPL"

    result = fuzzy_suggest_symbol("IAM")
    assert result == "IAM.SN"


def test_analyze_ticker_synthetic(tmp_path):
    cache = tmp_path / "data"
    res = analyze_ticker("AAA", source="synthetic", cache_dir=cache)
    assert res["symbol"] == "AAA"
    assert res["bars_count"] == 800
    assert res["events_count"] > 0
    assert res["summary"] is not None
    assert "hit_rate" in res["summary"]
    assert res["score_now"] is not None


def test_cli_analyze_command(tmp_path):
    runner = CliRunner()
    cache = tmp_path / "data"
    res = runner.invoke(app, ["analyze", "AAA", "--source", "synthetic", "--cache-dir", str(cache), "--explain"])
    assert res.exit_code == 0
    assert "REPORTE DE ANÁLISIS" in res.output
    assert "Tasa de Acierto" in res.output
    assert "Glosario y Conceptos" in res.output


def test_cli_report_edge_missing_data(tmp_path):
    """report edge sin datos previos debe dar mensaje amigable, no traceback."""
    runner = CliRunner()
    cache = tmp_path / "data_empty"
    res = runner.invoke(app, ["report", "edge", "--symbol", "NOEXISTE", "--cache-dir", str(cache)])
    assert res.exit_code == 1
    combined = res.output + (res.stderr if hasattr(res, 'stderr') and res.stderr else "")
    # Verificar que NO lanza un traceback crudo
    assert "Traceback" not in combined

