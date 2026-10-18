from pathlib import Path

from typer.testing import CliRunner

from tickerlab.cli.main import app


def test_pipeline_benchmark(benchmark, tmp_path: Path):
    runner = CliRunner()
    cache = tmp_path / "data"

    def run_pipeline():
        assert runner.invoke(app, ["ingest", "--symbol", "AAA", "--cache-dir", str(cache)]).exit_code == 0
        assert runner.invoke(app, ["features", "build", "--symbol", "AAA", "--cache-dir", str(cache)]).exit_code == 0
        assert runner.invoke(app, ["patterns", "scan", "--symbol", "AAA", "--cache-dir", str(cache)]).exit_code == 0
        assert runner.invoke(app, ["labels", "build", "--symbol", "AAA", "--cache-dir", str(cache)]).exit_code == 0
        assert runner.invoke(app, ["validate", "walkforward", "--symbol", "AAA", "--cache-dir", str(cache)]).exit_code == 0

    benchmark(run_pipeline)
