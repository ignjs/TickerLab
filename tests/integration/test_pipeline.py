from pathlib import Path

from typer.testing import CliRunner

from tickerlab.cli.main import app


def test_e2e_pipeline(tmp_path: Path):
    runner = CliRunner()
    cache = tmp_path / "data"

    assert runner.invoke(app, ["ingest", "--symbol", "AAA", "--cache-dir", str(cache)]).exit_code == 0
    assert runner.invoke(app, ["features", "build", "--symbol", "AAA", "--cache-dir", str(cache)]).exit_code == 0
    assert runner.invoke(app, ["patterns", "scan", "--symbol", "AAA", "--cache-dir", str(cache)]).exit_code == 0
    assert runner.invoke(app, ["labels", "build", "--symbol", "AAA", "--cache-dir", str(cache)]).exit_code == 0
    res = runner.invoke(app, ["validate", "walkforward", "--symbol", "AAA", "--cache-dir", str(cache)])
    assert res.exit_code == 0
    assert "validation=" in res.output
