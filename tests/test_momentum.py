"""Unit tests for Momentum and Oscillator indicators."""
import numpy as np
import pytest

from tradingview_indicators.momentum.aroon import aroon
from tradingview_indicators.momentum.connors_rsi import connors_rsi
from tradingview_indicators.momentum.elder_impulse import elder_impulse
from tradingview_indicators.momentum.fisher import fisher_transform
from tradingview_indicators.momentum.kama import kama
from tradingview_indicators.momentum.vortex import vortex
from tradingview_indicators.momentum.wavetrend import wavetrend


@pytest.fixture
def ohlc_data():
    np.random.seed(42)
    n = 120
    base = 100.0 + np.cumsum(np.random.randn(n) * 0.5)
    high = base + np.random.uniform(0.5, 2.0, n)
    low = base - np.random.uniform(0.5, 2.0, n)
    close = base + np.random.uniform(-0.4, 0.4, n)
    return high, low, close


def test_wavetrend(ohlc_data):
    high, low, close = ohlc_data
    res = wavetrend(high, low, close)
    assert len(res.wt1) == len(close)
    assert len(res.wt2) == len(close)
    assert np.isfinite(res.wt1[-1])
    assert np.isfinite(res.wt2[-1])


def test_connors_rsi(ohlc_data):
    _, _, close = ohlc_data
    res = connors_rsi(close, rsi_period=3, streak_period=2, rank_period=50)
    assert len(res.crsi) == len(close)
    assert np.isfinite(res.crsi[-1])
    # CRSI is bounded between 0 and 100
    valid_crsi = res.crsi[np.isfinite(res.crsi)]
    assert np.all(valid_crsi >= 0.0) and np.all(valid_crsi <= 100.0)


def test_vortex(ohlc_data):
    high, low, close = ohlc_data
    res = vortex(high, low, close, period=14)
    assert len(res.plus_vi) == len(close)
    assert len(res.minus_vi) == len(close)
    assert len(res.oscillator) == len(close)
    assert np.isfinite(res.oscillator[-1])


def test_fisher_transform(ohlc_data):
    high, low, _ = ohlc_data
    res = fisher_transform(high, low, period=10)
    assert len(res.fisher) == len(high)
    assert len(res.trigger) == len(high)
    assert np.isfinite(res.fisher[-1])


def test_aroon(ohlc_data):
    high, low, _ = ohlc_data
    res = aroon(high, low, period=25)
    assert len(res.aroon_up) == len(high)
    assert len(res.aroon_down) == len(high)
    valid_up = res.aroon_up[np.isfinite(res.aroon_up)]
    assert np.all(valid_up >= 0.0) and np.all(valid_up <= 100.0)


def test_kama(ohlc_data):
    _, _, close = ohlc_data
    res = kama(close, efficiency_period=10, fast_period=2, slow_period=30)
    assert len(res.kama) == len(close)
    assert np.isfinite(res.kama[-1])
    valid_er = res.efficiency_ratio[np.isfinite(res.efficiency_ratio)]
    assert np.all(valid_er >= 0.0) and np.all(valid_er <= 1.0)


def test_elder_impulse(ohlc_data):
    _, _, close = ohlc_data
    res = elder_impulse(close)
    assert len(res.state) == len(close)
    assert set(np.unique(res.state)).issubset({-1, 0, 1})
