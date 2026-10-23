"""Unit tests for Pine Script mathematical primitives."""
import numpy as np
import pytest

from tradingview_indicators.core.math import (
    cross_signals,
    crossed_over,
    crossed_under,
    moving_average,
    pine_ema,
    pine_hma,
    pine_rma,
    pine_rsi,
    pine_sma,
    pine_wma,
    true_range,
    var_ma,
    wilder_atr,
    zlema,
)


@pytest.fixture
def sample_series():
    return np.array([10.0, 11.0, 12.0, 11.5, 13.0, 14.0, 13.5, 15.0, 16.0, 15.5])


def test_pine_sma(sample_series):
    res = pine_sma(sample_series, 3)
    assert np.isnan(res[0])
    assert np.isnan(res[1])
    assert np.isclose(res[2], (10.0 + 11.0 + 12.0) / 3.0)
    assert np.isclose(res[3], (11.0 + 12.0 + 11.5) / 3.0)


def test_pine_ema(sample_series):
    res = pine_ema(sample_series, 3)
    assert res[0] == 10.0
    alpha = 2.0 / 4.0
    expected_1 = alpha * 11.0 + (1 - alpha) * 10.0
    assert np.isclose(res[1], expected_1)


def test_pine_rma(sample_series):
    res = pine_rma(sample_series, 3)
    assert np.isnan(res[0])
    assert np.isnan(res[1])
    seed = (10.0 + 11.0 + 12.0) / 3.0
    assert np.isclose(res[2], seed)
    alpha = 1.0 / 3.0
    expected_3 = alpha * 11.5 + (1 - alpha) * seed
    assert np.isclose(res[3], expected_3)


def test_pine_wma(sample_series):
    res = pine_wma(sample_series, 3)
    assert np.isnan(res[0])
    assert np.isnan(res[1])
    expected_2 = (10.0 * 1 + 11.0 * 2 + 12.0 * 3) / 6.0
    assert np.isclose(res[2], expected_2)


def test_pine_hma(sample_series):
    res = pine_hma(sample_series, 4)
    assert len(res) == len(sample_series)
    assert np.isfinite(res[-1])


def test_var_ma(sample_series):
    res = var_ma(sample_series, 5)
    assert len(res) == len(sample_series)
    assert np.isfinite(res[-1])


def test_zlema(sample_series):
    res = zlema(sample_series, 4)
    assert len(res) == len(sample_series)
    assert np.isfinite(res[-1])


def test_moving_average_dispatcher(sample_series):
    for ma_type in ["SMA", "EMA", "RMA", "WMA", "HMA", "VAR", "ZLEMA"]:
        res = moving_average(sample_series, ma_type, 3)
        assert len(res) == len(sample_series)

    with pytest.raises(ValueError):
        moving_average(sample_series, "UNKNOWN", 3)


def test_true_range_and_atr():
    high = np.array([12.0, 13.0, 12.5, 14.0])
    low = np.array([10.0, 11.0, 11.5, 12.0])
    close = np.array([11.0, 12.0, 12.0, 13.5])

    tr = true_range(high, low, close)
    assert np.isclose(tr[0], 2.0)
    # bar 1: max(13-11=2, |13-11|=2, |11-11|=0) -> 2.0
    assert np.isclose(tr[1], 2.0)

    atr = wilder_atr(high, low, close, period=2)
    assert np.isnan(atr[0])
    assert np.isclose(atr[1], 2.0)


def test_cross_signals():
    left = np.array([1.0, 3.0, 2.0, 5.0])
    right = np.array([2.0, 2.0, 4.0, 4.0])

    up, down = cross_signals(left, right)
    # index 1: left crossed above right (1->3 vs 2->2)
    assert up[1] == True
    assert down[1] == False
    # index 2: left crossed below right (3->2 vs 2->4)
    assert up[2] == False
    assert down[2] == True

    assert crossed_over(left, right)[1] == True
    assert crossed_under(left, right)[2] == True


def test_pine_rsi():
    close = np.linspace(10.0, 20.0, 30)
    rsi = pine_rsi(close, 14)
    # Steady upward progression should result in high RSI (>70)
    assert np.isfinite(rsi[-1])
    assert rsi[-1] > 70.0
