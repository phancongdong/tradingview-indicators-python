"""Olivier Seban's canonical SuperTrend indicator ported from TradingView Pine Script (ta.supertrend).

Calculates dynamic volatility bands using Wilder's ATR and maintains the recursive
band ratchet mechanism for trailing stops.
"""
from __future__ import annotations

import math
import numpy as np

from tradingview_indicators.core.math import wilder_atr
from tradingview_indicators.core.types import SuperTrendResult


def supertrend(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    period: int = 10,
    factor: float = 3.0,
) -> SuperTrendResult:
    """Compute TradingView's canonical SuperTrend indicator.

    Parameters:
        high: High price series.
        low: Low price series.
        close: Close price series.
        period: ATR calculation period (default: 10).
        factor: ATR multiplier factor (default: 3.0).

    Returns:
        SuperTrendResult with supertrend line, direction (1 = Bullish, -1 = Bearish),
        upper/lower bands, and crossover buy/sell signals.
    """
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    c = np.asarray(close, dtype=float)
    n = len(c)

    atr = wilder_atr(h, l, c, period)
    hl2 = (h + l) / 2.0
    basic_upper = hl2 + factor * atr
    basic_lower = hl2 - factor * atr

    final_upper = np.full(n, np.nan, dtype=float)
    final_lower = np.full(n, np.nan, dtype=float)
    supertrend_line = np.full(n, np.nan, dtype=float)
    # direction: 1 for Bullish/Uptrend, -1 for Bearish/Downtrend
    direction = np.zeros(n, dtype=np.int8)

    for idx in range(n):
        if not math.isfinite(atr[idx]):
            continue

        if idx == 0 or not math.isfinite(final_upper[idx - 1]):
            final_upper[idx] = basic_upper[idx]
            final_lower[idx] = basic_lower[idx]
            direction[idx] = 1 if c[idx] >= hl2[idx] else -1
            supertrend_line[idx] = final_lower[idx] if direction[idx] == 1 else final_upper[idx]
            continue

        prev_upper = final_upper[idx - 1]
        prev_lower = final_lower[idx - 1]

        final_lower[idx] = (
            basic_lower[idx]
            if basic_lower[idx] > prev_lower or c[idx - 1] < prev_lower
            else prev_lower
        )
        final_upper[idx] = (
            basic_upper[idx]
            if basic_upper[idx] < prev_upper or c[idx - 1] > prev_upper
            else prev_upper
        )

        prev_supertrend = supertrend_line[idx - 1]
        # In Pine Script: if prev_supertrend == prev_upper (bearish state)
        if math.isclose(prev_supertrend, prev_upper, rel_tol=0.0, abs_tol=1e-12):
            direction[idx] = 1 if c[idx] > final_upper[idx] else -1
        else:
            direction[idx] = -1 if c[idx] < final_lower[idx] else 1

        supertrend_line[idx] = final_lower[idx] if direction[idx] == 1 else final_upper[idx]

    # Generate entry signals on direction flips
    buy_signal = np.zeros(n, dtype=bool)
    sell_signal = np.zeros(n, dtype=bool)
    if n > 1:
        buy_signal[1:] = (direction[1:] == 1) & (direction[:-1] == -1)
        sell_signal[1:] = (direction[1:] == -1) & (direction[:-1] == 1)

    return SuperTrendResult(
        supertrend=supertrend_line,
        direction=direction,
        upper_band=final_upper,
        lower_band=final_lower,
        buy_signal=buy_signal,
        sell_signal=sell_signal,
    )
