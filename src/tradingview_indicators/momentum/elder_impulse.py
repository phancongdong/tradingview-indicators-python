"""Alexander Elder's Impulse System ported from TradingView Pine Script.

Combines an Exponential Moving Average (measuring trend inertia) and MACD Histogram
(measuring market power) to color bars Bullish (Green), Bearish (Red), or Neutral (Blue).
"""
from __future__ import annotations

import numpy as np

from tradingview_indicators.core.math import pine_ema
from tradingview_indicators.core.types import ElderImpulseResult


def elder_impulse(
    close: np.ndarray,
    ema_period: int = 13,
    macd_fast: int = 12,
    macd_slow: int = 26,
    signal_period: int = 9,
) -> ElderImpulseResult:
    """Compute Elder Impulse System.

    Parameters:
        close: Close price series.
        ema_period: EMA trend length (default: 13).
        macd_fast: Fast MACD EMA length (default: 12).
        macd_slow: Slow MACD EMA length (default: 26).
        signal_period: MACD signal line EMA length (default: 9).

    Returns:
        ElderImpulseResult with state (1 = Bullish/Green, -1 = Bearish/Red, 0 = Neutral/Blue),
        ema, and macd_hist.
    """
    c = np.asarray(close, dtype=float)
    n = len(c)

    trend_ema = pine_ema(c, ema_period)
    fast_ema = pine_ema(c, macd_fast)
    slow_ema = pine_ema(c, macd_slow)
    macd_line = fast_ema - slow_ema
    signal_line = pine_ema(macd_line, signal_period)
    macd_hist = macd_line - signal_line

    state = np.zeros(n, dtype=np.int8)

    if n > 1:
        ema_rising = trend_ema[1:] > trend_ema[:-1]
        ema_falling = trend_ema[1:] < trend_ema[:-1]
        hist_rising = macd_hist[1:] > macd_hist[:-1]
        hist_falling = macd_hist[1:] < macd_hist[:-1]

        bullish = ema_rising & hist_rising
        bearish = ema_falling & hist_falling

        state[1:][bullish] = 1
        state[1:][bearish] = -1

    return ElderImpulseResult(
        state=state,
        ema=trend_ema,
        macd_hist=macd_hist,
    )
