"""Mihkel00's SSL Hybrid channel & baseline indicator ported from Pine Script (2it69GUx).

SSL Hybrid creates dynamic support and resistance channels using high and low price
moving averages (typically HMA or EMA), identifying trend bias and structural breakouts.
"""
from __future__ import annotations

import math
import numpy as np

from tradingview_indicators.core.math import cross_signals, moving_average
from tradingview_indicators.core.types import SSLHybridResult


def ssl_hybrid(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    ssl_length: int = 10,
    ma_type: str = "HMA",
) -> SSLHybridResult:
    """Compute Mihkel00's SSL Hybrid channel and trend state.

    Parameters:
        high: High price series.
        low: Low price series.
        close: Close price series.
        ssl_length: Moving average period for High/Low bands (default: 10).
        ma_type: Moving average type ('HMA', 'EMA', 'SMA', 'WMA').

    Returns:
        SSLHybridResult with ssl_down line, hlv direction state, bands, and crossover signals.
    """
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    c = np.asarray(close, dtype=float)
    n = len(c)

    ma_high = moving_average(h, ma_type, ssl_length)
    ma_low = moving_average(l, ma_type, ssl_length)

    hlv = np.zeros(n, dtype=np.int8)
    state = 0

    for idx in range(n):
        if math.isfinite(ma_high[idx]) and c[idx] > ma_high[idx]:
            state = 1
        elif math.isfinite(ma_low[idx]) and c[idx] < ma_low[idx]:
            state = -1
        hlv[idx] = state

    ssl_down = np.full(n, np.nan, dtype=float)
    bullish = hlv > 0
    bearish = hlv < 0
    ssl_down[bullish] = ma_low[bullish]
    ssl_down[bearish] = ma_high[bearish]

    cross_up, cross_down = cross_signals(c, ssl_down)

    return SSLHybridResult(
        ssl_down=ssl_down,
        hlv=hlv,
        ma_high=ma_high,
        ma_low=ma_low,
        cross_up=cross_up,
        cross_down=cross_down,
    )
