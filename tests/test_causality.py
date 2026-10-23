"""Point-in-time causality tests to ensure zero lookahead bias across all indicators."""
import numpy as np
import pytest

from tradingview_indicators.breakout.ut_bot import ut_bot
from tradingview_indicators.momentum.wavetrend import wavetrend
from tradingview_indicators.trend.alphatrend import alphatrend
from tradingview_indicators.trend.ott import ott
from tradingview_indicators.trend.pmax import pmax
from tradingview_indicators.trend.supertrend import supertrend


@pytest.fixture
def sequence_data():
    np.random.seed(123)
    n = 150
    base = 50.0 + np.cumsum(np.random.randn(n) * 0.4)
    high = base + np.random.uniform(0.5, 1.5, n)
    low = base - np.random.uniform(0.5, 1.5, n)
    close = base + np.random.uniform(-0.3, 0.3, n)
    volume = np.random.uniform(500.0, 5000.0, n)
    return high, low, close, volume


def test_alphatrend_causality(sequence_data):
    high, low, close, volume = sequence_data
    t = 80
    res_short = alphatrend(high[:t], low[:t], close[:t], volume[:t], period=14, oscillator="MFI")
    res_full = alphatrend(high, low, close, volume, period=14, oscillator="MFI")
    # Bar t-1 must be identical
    assert np.isclose(res_short.alpha_trend[t - 1], res_full.alpha_trend[t - 1], equal_nan=True)


def test_ott_causality(sequence_data):
    _, _, close, _ = sequence_data
    t = 80
    res_short = ott(close[:t], period=14, percent=1.0)
    res_full = ott(close, period=14, percent=1.0)
    assert np.isclose(res_short.ott[t - 1], res_full.ott[t - 1], equal_nan=True)


def test_supertrend_causality(sequence_data):
    high, low, close, _ = sequence_data
    t = 80
    res_short = supertrend(high[:t], low[:t], close[:t], period=10, factor=3.0)
    res_full = supertrend(high, low, close, period=10, factor=3.0)
    assert np.isclose(res_short.supertrend[t - 1], res_full.supertrend[t - 1], equal_nan=True)
    assert res_short.direction[t - 1] == res_full.direction[t - 1]


def test_ut_bot_causality(sequence_data):
    high, low, close, _ = sequence_data
    t = 80
    res_short = ut_bot(close[:t], high[:t], low[:t], sensitivity=1.0, atr_period=10)
    res_full = ut_bot(close, high, low, sensitivity=1.0, atr_period=10)
    assert np.isclose(res_short.stop[t - 1], res_full.stop[t - 1], equal_nan=True)


def test_wavetrend_causality(sequence_data):
    high, low, close, _ = sequence_data
    t = 80
    res_short = wavetrend(high[:t], low[:t], close[:t])
    res_full = wavetrend(high, low, close)
    assert np.isclose(res_short.wt1[t - 1], res_full.wt1[t - 1], equal_nan=True)
    assert np.isclose(res_short.wt2[t - 1], res_full.wt2[t - 1], equal_nan=True)
