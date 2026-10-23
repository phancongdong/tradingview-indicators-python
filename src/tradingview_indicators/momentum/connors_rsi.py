"""Larry Connors RSI-3 composite momentum indicator.

Combines standard Wilder RSI of price, RSI of the directional streak length,
and a rolling percentile rank of 1-day rate-of-change into a 0-100 oscillator.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from tradingview_indicators.core.math import pine_rsi
from tradingview_indicators.core.types import ConnorsRSIResult


def price_streak(close: np.ndarray) -> np.ndarray:
    """Calculate consecutive directional price closing streaks.

    Positive streak count for consecutive up closes; negative count for down closes.
    """
    c = np.asarray(close, dtype=float)
    n = len(c)
    streak = np.zeros(n, dtype=float)
    if n <= 1:
        return streak

    diffs = np.diff(c)
    directions = np.sign(diffs)

    current_streak = 0.0
    for idx in range(1, n):
        d = directions[idx - 1]
        if d > 0:
            current_streak = current_streak + 1.0 if current_streak > 0 else 1.0
        elif d < 0:
            current_streak = current_streak - 1.0 if current_streak < 0 else -1.0
        else:
            current_streak = 0.0
        streak[idx] = current_streak
    return streak


def rolling_percent_rank(values: np.ndarray, period: int = 100) -> np.ndarray:
    """Compute rolling percentile rank over the trailing `period` observations."""
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    result = np.full(n, np.nan, dtype=float)
    for idx in range(period, n):
        val = arr[idx]
        window = arr[idx - period : idx]
        finite_window = window[np.isfinite(window)]
        if np.isfinite(val) and len(finite_window) > 0:
            result[idx] = float(np.mean(finite_window < val) * 100.0)
    return result


def connors_rsi(
    close: np.ndarray,
    rsi_period: int = 3,
    streak_period: int = 2,
    rank_period: int = 100,
) -> ConnorsRSIResult:
    """Compute Larry Connors RSI-3.

    Parameters:
        close: Close price series.
        rsi_period: Lookback period for price RSI (default: 3).
        streak_period: Lookback period for streak RSI (default: 2).
        rank_period: Lookback period for rolling percent rank (default: 100).

    Returns:
        ConnorsRSIResult containing composite crsi, rsi, streak_rsi, and percent_rank.
    """
    c = np.asarray(close, dtype=float)

    price_rsi_val = pine_rsi(c, rsi_period)
    streaks = price_streak(c)
    streak_rsi_val = pine_rsi(streaks, streak_period)

    # Calculate 1-period percentage returns for percent rank
    returns = np.full(len(c), np.nan, dtype=float)
    if len(c) > 1:
        prev = c[:-1]
        returns[1:] = np.where(prev != 0.0, (c[1:] - prev) / prev, 0.0)

    rank_val = rolling_percent_rank(returns, rank_period)
    crsi = (price_rsi_val + streak_rsi_val + rank_val) / 3.0

    return ConnorsRSIResult(
        crsi=crsi,
        rsi=price_rsi_val,
        streak_rsi=streak_rsi_val,
        percent_rank=rank_val,
    )
