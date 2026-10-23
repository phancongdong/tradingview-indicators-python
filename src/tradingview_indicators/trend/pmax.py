"""Kıvanç Özbilgiç's Profit Maximizer (PMax) ported from TradingView Pine Script (v6Ws9H9j).

PMax combines a moving average with an ATR-based dynamic volatility trailing stop band,
providing robust trend-following signals and stop-and-reverse capabilities.
"""
from __future__ import annotations

import math
import numpy as np

from tradingview_indicators.core.math import (
    cross_signals,
    moving_average,
    wilder_atr,
)
from tradingview_indicators.core.types import PMaxResult


def pmax(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    ma_length: int = 10,
    atr_length: int = 10,
    multiplier: float = 3.0,
    ma_type: str = "EMA",
) -> PMaxResult:
    """Compute Kıvanç Özbilgiç's Profit Maximizer (PMax).

    Parameters:
        high: High price series.
        low: Low price series.
        close: Close price series.
        ma_length: Base moving average length (default: 10).
        atr_length: ATR calculation length (default: 10).
        multiplier: ATR channel expansion multiplier (default: 3.0).
        ma_type: Moving average type ('EMA', 'SMA', 'WMA', 'HMA', 'VAR', 'ZLEMA').

    Returns:
        PMaxResult containing pmax, mavg, long_stop, short_stop, direction, and signals.
    """
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    c = np.asarray(close, dtype=float)
    n = len(c)

    mavg = moving_average(c, ma_type=ma_type, length=ma_length)
    atr = wilder_atr(h, l, c, period=atr_length)

    long_stop = np.full(n, np.nan, dtype=float)
    short_stop = np.full(n, np.nan, dtype=float)
    direction = np.ones(n, dtype=int)
    pmax_line = np.full(n, np.nan, dtype=float)

    for idx in range(n):
        if not (math.isfinite(mavg[idx]) and math.isfinite(atr[idx])):
            direction[idx] = direction[idx - 1] if idx > 0 else 1
            continue

        raw_long = float(mavg[idx]) - multiplier * float(atr[idx])
        raw_short = float(mavg[idx]) + multiplier * float(atr[idx])

        prev_long = float(long_stop[idx - 1]) if idx > 0 and math.isfinite(long_stop[idx - 1]) else raw_long
        prev_short = float(short_stop[idx - 1]) if idx > 0 and math.isfinite(short_stop[idx - 1]) else raw_short

        long_stop[idx] = max(raw_long, prev_long) if mavg[idx] > prev_long else raw_long
        short_stop[idx] = min(raw_short, prev_short) if mavg[idx] < prev_short else raw_short

        prev_dir = int(direction[idx - 1]) if idx > 0 else 1
        if prev_dir == -1 and mavg[idx] > prev_short:
            curr_dir = 1
        elif prev_dir == 1 and mavg[idx] < prev_long:
            curr_dir = -1
        else:
            curr_dir = prev_dir

        direction[idx] = curr_dir
        pmax_line[idx] = long_stop[idx] if curr_dir == 1 else short_stop[idx]

    buy_signal, sell_signal = cross_signals(mavg, pmax_line)

    return PMaxResult(
        pmax=pmax_line,
        mavg=mavg,
        long_stop=long_stop,
        short_stop=short_stop,
        direction=direction,
        buy_signal=buy_signal,
        sell_signal=sell_signal,
    )
