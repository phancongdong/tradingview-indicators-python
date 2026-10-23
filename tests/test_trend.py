"""Unit tests for Trend Indicators (AlphaTrend, OTT, PMax, SuperTrend)."""
import numpy as np
import pytest

from tradingview_indicators.trend.alphatrend import alphatrend
from tradingview_indicators.trend.ott import ott
from tradingview_indicators.trend.pmax import pmax
from tradingview_indicators.trend.supertrend import supertrend


@pytest.fixture
def ohlcv_data():
    np.random.seed(42)
    n = 100
    base = 100.0 + np.cumsum(np.random.randn(n) * 0.5)
    high = base + np.random.uniform(0.5, 2.0, n)
    low = base - np.random.uniform(0.5, 2.0, n)
    close = base + np.random.uniform(-0.4, 0.4, n)
    volume = np.random.uniform(100.0, 1000.0, n)
    return high, low, close, volume


def test_alphatrend(ohlcv_data):
    high, low, close, volume = ohlcv_data
    # Test with MFI
    res_mfi = alphatrend(high, low, close, volume=volume, period=14, multiplier=1.0, oscillator="MFI")
    assert len(res_mfi.alpha_trend) == len(close)
    assert len(res_mfi.buy_signal) == len(close)
    assert np.isfinite(res_mfi.alpha_trend[-1])

    # Test with RSI (no volume needed)
    res_rsi = alphatrend(high, low, close, period=14, multiplier=1.0, oscillator="RSI")
    assert len(res_rsi.alpha_trend) == len(close)
    assert np.isfinite(res_rsi.alpha_trend[-1])


def test_ott(ohlcv_data):
    _, _, close, _ = ohlcv_data
    res = ott(close, period=14, percent=1.0, ma_type="VAR")
    assert len(res.ott) == len(close)
    assert len(res.direction) == len(close)
    assert set(np.unique(res.direction)).issubset({-1, 1})
    assert np.isfinite(res.ott[-1])
    assert np.isfinite(res.mt[-1])


def test_pmax(ohlcv_data):
    high, low, close, _ = ohlcv_data
    res = pmax(high, low, close, ma_length=10, atr_length=10, multiplier=3.0, ma_type="EMA")
    assert len(res.pmax) == len(close)
    assert len(res.direction) == len(close)
    assert set(np.unique(res.direction)).issubset({-1, 1})
    assert np.isfinite(res.pmax[-1])


def test_supertrend(ohlcv_data):
    high, low, close, _ = ohlcv_data
    res = supertrend(high, low, close, period=10, factor=3.0)
    assert len(res.supertrend) == len(close)
    assert len(res.direction) == len(close)
    valid_dir = res.direction[np.isfinite(res.supertrend)]
    assert set(np.unique(valid_dir)).issubset({-1, 1})
    assert np.isfinite(res.supertrend[-1])
    # Signals are mutually exclusive at any single bar
    assert not np.any(res.buy_signal & res.sell_signal)
