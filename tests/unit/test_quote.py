from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from tickerlab.cli.main import app
from tickerlab.ingest.service import get_realtime_quote


def test_get_realtime_quote_mocked():
    runner = CliRunner()
    fake_fast_info = MagicMock()
    fake_fast_info.last_price = 105.5
    fake_fast_info.previous_close = 100.0
    fake_fast_info.open = 101.0
    fake_fast_info.day_high = 106.0
    fake_fast_info.day_low = 100.5
    fake_fast_info.last_volume = 1234567
    fake_fast_info.currency = "USD"
    fake_fast_info.timezone = "America/New_York"

    with patch("yfinance.Ticker") as mock_ticker:
        mock_instance = MagicMock()
        mock_instance.fast_info = fake_fast_info
        mock_ticker.return_value = mock_instance

        q = get_realtime_quote("AAPL")
        assert q["symbol"] == "AAPL"
        assert q["price"] == 105.5
        assert round(q["change"], 1) == 5.5
        assert round(q["change_pct"], 1) == 5.5
        assert q["currency"] == "USD"

        # Test CLI command
        res = runner.invoke(app, ["quote", "AAPL"])
        assert res.exit_code == 0
        assert "AAPL" in res.output
        assert "105.50" in res.output
