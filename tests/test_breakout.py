"""Unit tests for Breakout Indicators (UT Bot, SSL Hybrid)."""
import numpy as np
import pytest

from tradingview_indicators.breakout.ssl_hybrid import ssl_hybrid
from tradingview_indicators.breakout.ut_bot import ut_bot


@pytest.fixture
def ohlcv_data():
    np.random.seed(42)
    n = 80
    base = 100.0 + np.cumsum(np.random.randn(n) * 0.5)
    high = base + np.random.uniform(0.5, 2.0, n)
    low = base - np.random.uniform(0.5, 2.0, n)
    close = base + np.random.uniform(-0.4, 0.4, n)
    return high, low, close


def test_ut_bot(ohlcv_data):
    high, low, close = ohlcv_data
    res = ut_bot(close, high, low, sensitivity=1.5, atr_period=10)
    assert len(res.stop) == len(close)
    assert len(res.buy_signal) == len(close)
    assert len(res.sell_signal) == len(close)
    assert np.isfinite(res.stop[-1])
    assert not np.any(res.buy_signal & res.sell_signal)


def test_ssl_hybrid(ohlcv_data):
    high, low, close = ohlcv_data
    res = ssl_hybrid(high, low, close, ssl_length=10, ma_type="HMA")
    assert len(res.ssl_down) == len(close)
    assert len(res.hlv) == len(close)
    assert set(np.unique(res.hlv)).issubset({-1, 0, 1})
    assert np.isfinite(res.ssl_down[-1])
