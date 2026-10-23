"""Kıvanç Özbilgiç's Optimized Trend Tracker (OTT) ported from Pine Script (ycDUERPO).

OTT utilizes an adaptive variable moving average (VAR MA / VIDYA) filtered through
a dual-state trailing stop (Master Trend) and percentage-offset envelope.
"""
from __future__ import annotations

import math
import numpy as np

from tradingview_indicators.core.math import cross_signals, moving_average
from tradingview_indicators.core.types import OTTResult


def ott(
    source: np.ndarray,
    period: int = 14,
    percent: float = 1.0,
    ma_type: str = "VAR",
) -> OTTResult:
    """Compute Kıvanç Özbilgiç's Optimized Trend Tracker (OTT).

    Parameters:
        source: Price series to track (typically close or hlc3).
        period: Moving average lookback period (default: 14).
        percent: Channel width percentage offset (default: 1.0).
        ma_type: Base moving average type ('VAR', 'EMA', 'SMA', 'WMA', 'HMA', 'ZLEMA').

    Returns:
        OTTResult containing ott, mt, variable_ma, trailing stops, direction, and signals.
    """
    src = np.asarray(source, dtype=float)
    n = len(src)

    variable = moving_average(src, ma_type=ma_type, length=period)

    fraction = percent * 0.01
    long_stop = np.full(n, np.nan, dtype=float)
    short_stop = np.full(n, np.nan, dtype=float)
    direction = np.ones(n, dtype=np.int8)
    mt = np.full(n, np.nan, dtype=float)
    ott_line = np.full(n, np.nan, dtype=float)

    for idx in range(n):
        if not math.isfinite(variable[idx]):
            direction[idx] = direction[idx - 1] if idx > 0 else 1
            continue

        raw_long = float(variable[idx]) * (1.0 - fraction)
        raw_short = float(variable[idx]) * (1.0 + fraction)

        prev_long = float(long_stop[idx - 1]) if idx > 0 and math.isfinite(long_stop[idx - 1]) else raw_long
        prev_short = float(short_stop[idx - 1]) if idx > 0 and math.isfinite(short_stop[idx - 1]) else raw_short

        long_stop[idx] = max(raw_long, prev_long) if variable[idx] > prev_long else raw_long
        short_stop[idx] = min(raw_short, prev_short) if variable[idx] < prev_short else raw_short

        prev_dir = int(direction[idx - 1]) if idx > 0 else 1
        if prev_dir == -1 and variable[idx] > prev_short:
            curr_dir = 1
        elif prev_dir == 1 and variable[idx] < prev_long:
            curr_dir = -1
        else:
            curr_dir = prev_dir

        direction[idx] = curr_dir
        mt[idx] = long_stop[idx] if curr_dir == 1 else short_stop[idx]

        if variable[idx] > mt[idx]:
            ott_line[idx] = mt[idx] * (200.0 + percent) / 200.0
        else:
            ott_line[idx] = mt[idx] * (200.0 - percent) / 200.0

    buy_signal, sell_signal = cross_signals(variable, ott_line)

    return OTTResult(
        ott=ott_line,
        mt=mt,
        variable_ma=variable,
        long_stop=long_stop,
        short_stop=short_stop,
        direction=direction,
        buy_signal=buy_signal,
        sell_signal=sell_signal,
    )
