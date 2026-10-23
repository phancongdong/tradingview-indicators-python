"""Aroon Indicator and Oscillator ported from TradingView Pine Script.

Tracks the number of periods elapsed since the highest high and lowest low to identify
emerging trends and consolidation regimes.
"""
from __future__ import annotations

import numpy as np

from tradingview_indicators.core.types import AroonResult


def aroon(
    high: np.ndarray,
    low: np.ndarray,
    period: int = 25,
) -> AroonResult:
    """Compute Aroon Indicator and Oscillator.

    Parameters:
        high: High price series.
        low: Low price series.
        period: Lookback window (default: 25).

    Returns:
        AroonResult containing aroon_up, aroon_down, and aroon_oscillator.
    """
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    n = len(h)

    aroon_up = np.full(n, np.nan, dtype=float)
    aroon_down = np.full(n, np.nan, dtype=float)

    for idx in range(period, n):
        window_high = h[idx - period : idx + 1]
        window_low = l[idx - period : idx + 1]

        bars_since_high = len(window_high) - 1 - int(np.argmax(window_high))
        bars_since_low = len(window_low) - 1 - int(np.argmin(window_low))

        aroon_up[idx] = 100.0 * (period - bars_since_high) / period
        aroon_down[idx] = 100.0 * (period - bars_since_low) / period

    oscillator = aroon_up - aroon_down

    return AroonResult(
        aroon_up=aroon_up,
        aroon_down=aroon_down,
        oscillator=oscillator,
    )
