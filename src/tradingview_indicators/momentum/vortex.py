"""Vortex Indicator (VI+ / VI-) ported from TradingView Pine Script.

Measures directional trend movement based on the distance between current bar highs/lows
and previous bar lows/highs, normalized by True Range.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from tradingview_indicators.core.math import true_range
from tradingview_indicators.core.types import VortexResult


def vortex(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    period: int = 14,
) -> VortexResult:
    """Compute Vortex Indicator.

    Parameters:
        high: High price series.
        low: Low price series.
        close: Close price series.
        period: Lookback window for Vortex summation (default: 14).

    Returns:
        VortexResult containing plus_vi, minus_vi, and oscillator (plus_vi - minus_vi).
    """
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    c = np.asarray(close, dtype=float)
    n = len(c)

    tr = true_range(h, l, c)
    tr_sum = pd.Series(tr).rolling(period, min_periods=period).sum().to_numpy(dtype=float)

    plus_vm = np.full(n, np.nan, dtype=float)
    minus_vm = np.full(n, np.nan, dtype=float)

    if n > 1:
        plus_vm[1:] = np.abs(h[1:] - l[:-1])
        minus_vm[1:] = np.abs(l[1:] - h[:-1])

    vm_plus_sum = pd.Series(plus_vm).rolling(period, min_periods=period).sum().to_numpy(dtype=float)
    vm_minus_sum = pd.Series(minus_vm).rolling(period, min_periods=period).sum().to_numpy(dtype=float)

    denom = np.where(tr_sum == 0.0, np.nan, tr_sum)
    plus_vi = vm_plus_sum / denom
    minus_vi = vm_minus_sum / denom
    oscillator = plus_vi - minus_vi

    return VortexResult(
        plus_vi=plus_vi,
        minus_vi=minus_vi,
        oscillator=oscillator,
    )
