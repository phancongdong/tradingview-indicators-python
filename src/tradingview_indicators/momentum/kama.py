"""Perry Kaufman's Adaptive Moving Average (KAMA) ported from Pine Script.

Dynamically adjusts smoothing speed based on the market Efficiency Ratio (ER),
slowing down during noisy consolidation and accelerating in directional trends.
"""
from __future__ import annotations

import math
import numpy as np
import pandas as pd

from tradingview_indicators.core.types import KAMAResult


def kama(
    close: np.ndarray,
    efficiency_period: int = 10,
    fast_period: int = 2,
    slow_period: int = 30,
) -> KAMAResult:
    """Compute Kaufman Adaptive Moving Average (KAMA).

    Parameters:
        close: Close price series.
        efficiency_period: Lookback window for market direction and volatility (default: 10).
        fast_period: Fast EMA period (default: 2).
        slow_period: Slow EMA period (default: 30).

    Returns:
        KAMAResult containing the kama series and efficiency_ratio.
    """
    c = np.asarray(close, dtype=float)
    n = len(c)

    change = np.full(n, np.nan, dtype=float)
    if n > efficiency_period:
        change[efficiency_period:] = np.abs(c[efficiency_period:] - c[:-efficiency_period])

    deltas = np.full(n, np.nan, dtype=float)
    if n > 1:
        deltas[1:] = np.abs(c[1:] - c[:-1])

    volatility = pd.Series(deltas).rolling(efficiency_period, min_periods=efficiency_period).sum().to_numpy(dtype=float)

    er = np.zeros(n, dtype=float)
    valid_vol = np.isfinite(volatility) & (volatility > 0.0)
    er[valid_vol] = change[valid_vol] / volatility[valid_vol]

    fast_sc = 2.0 / (fast_period + 1.0)
    slow_sc = 2.0 / (slow_period + 1.0)
    smoothing_factor = (er * (fast_sc - slow_sc) + slow_sc) ** 2

    kama_series = np.full(n, np.nan, dtype=float)
    prior = math.nan

    for idx in range(n):
        if not math.isfinite(c[idx]):
            continue
        sc = smoothing_factor[idx]
        if not math.isfinite(prior):
            prior = float(c[idx])
        elif math.isfinite(sc):
            prior = prior + sc * (float(c[idx]) - prior)
        kama_series[idx] = prior

    return KAMAResult(
        kama=kama_series,
        efficiency_ratio=er,
    )
