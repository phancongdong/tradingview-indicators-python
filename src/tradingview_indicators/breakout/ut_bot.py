"""QuantNomad's UT Bot Alerts trailing stop indicator ported from Pine Script (VKMgZdYr).

UT Bot uses an ATR-scaled trailing volatility stop that dynamically snaps between
support floor and resistance ceiling to generate high-probability breakout alerts.
"""
from __future__ import annotations

import math
import numpy as np

from tradingview_indicators.core.math import cross_signals, wilder_atr
from tradingview_indicators.core.types import UTBotResult


def ut_bot(
    close: np.ndarray,
    high: np.ndarray | None = None,
    low: np.ndarray | None = None,
    sensitivity: float = 1.0,
    atr_period: int = 10,
) -> UTBotResult:
    """Compute QuantNomad's UT Bot Alerts trailing stop.

    Parameters:
        close: Close price series.
        high: High price series (optional; if None, close is used for ATR proxy).
        low: Low price series (optional; if None, close is used for ATR proxy).
        sensitivity: Sensitivity multiplier for the ATR trailing stop (default: 1.0).
        atr_period: ATR lookback period (default: 10).

    Returns:
        UTBotResult containing trailing stop series and buy/sell signals.
    """
    c = np.asarray(close, dtype=float)
    h = np.asarray(high if high is not None else c, dtype=float)
    l = np.asarray(low if low is not None else c, dtype=float)
    n = len(c)

    atr = wilder_atr(h, l, c, atr_period)
    stop = np.full(n, np.nan, dtype=float)

    for idx in range(n):
        if not math.isfinite(atr[idx]):
            continue

        prev_stop = float(stop[idx - 1]) if idx > 0 and math.isfinite(stop[idx - 1]) else 0.0
        prev_close = float(c[idx - 1]) if idx > 0 else c[idx]
        loss = sensitivity * float(atr[idx])

        if c[idx] > prev_stop and prev_close > prev_stop:
            stop[idx] = max(prev_stop, float(c[idx]) - loss)
        elif c[idx] < prev_stop and prev_close < prev_stop:
            stop[idx] = min(prev_stop, float(c[idx]) + loss)
        elif c[idx] > prev_stop:
            stop[idx] = float(c[idx]) - loss
        else:
            stop[idx] = float(c[idx]) + loss

    cross_up, cross_down = cross_signals(c, stop)
    buy_signal = cross_up & (c > stop)
    sell_signal = cross_down & (c < stop)

    return UTBotResult(
        stop=stop,
        buy_signal=buy_signal,
        sell_signal=sell_signal,
    )
