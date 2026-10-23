"""Kıvanç Özbilgiç's AlphaTrend indicator ported from TradingView Pine Script (3wdQu7P3).

AlphaTrend is a trend-following dynamic stop/line that adapts to volatility (via ATR)
and market momentum/volume flow (via MFI or RSI).
"""
from __future__ import annotations

import math
import numpy as np
import pandas as pd

from tradingview_indicators.core.math import (
    cross_signals,
    pine_rsi,
    pine_sma,
    true_range,
)
from tradingview_indicators.core.types import AlphaTrendResult


def pine_mfi(source: np.ndarray, volume: np.ndarray, length: int) -> np.ndarray:
    """TradingView ta.mfi: Money Flow Index."""
    src = np.asarray(source, dtype=float)
    vol = np.asarray(volume, dtype=float)
    changes = np.full(len(src), np.nan, dtype=float)
    changes[1:] = src[1:] - src[:-1]
    raw_flow = src * vol
    positive = np.where(changes > 0.0, raw_flow, 0.0)
    negative = np.where(changes < 0.0, raw_flow, 0.0)
    positive[0] = np.nan
    negative[0] = np.nan
    pos_sum = pd.Series(positive).rolling(length, min_periods=length).sum().to_numpy(dtype=float)
    neg_sum = pd.Series(negative).rolling(length, min_periods=length).sum().to_numpy(dtype=float)
    result = np.full(len(src), np.nan, dtype=float)
    finite = np.isfinite(pos_sum) & np.isfinite(neg_sum)
    result[finite & (pos_sum == 0.0) & (neg_sum == 0.0)] = 50.0
    result[finite & (pos_sum > 0.0) & (neg_sum == 0.0)] = 100.0
    result[finite & (pos_sum == 0.0) & (neg_sum > 0.0)] = 0.0
    regular = finite & (pos_sum > 0.0) & (neg_sum > 0.0)
    ratio = pos_sum[regular] / neg_sum[regular]
    result[regular] = 100.0 - 100.0 / (1.0 + ratio)
    return result


def alphatrend(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray | None = None,
    period: int = 14,
    multiplier: float = 1.0,
    oscillator: str = "MFI",
) -> AlphaTrendResult:
    """Compute Kıvanç Özbilgiç's AlphaTrend indicator.

    Parameters:
        high: High price series.
        low: Low price series.
        close: Close price series.
        volume: Volume series (required if oscillator is 'MFI').
        period: ATR and momentum calculation lookback window (default: 14).
        multiplier: Volatility expansion multiplier (default: 1.0).
        oscillator: 'MFI' (Money Flow Index with volume) or 'RSI' (Relative Strength Index).

    Returns:
        AlphaTrendResult containing alpha_trend, line_2 (2-bar lag), thresholds, and signals.
    """
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    c = np.asarray(close, dtype=float)
    n = len(c)

    tr = true_range(h, l, c)
    atr = pine_sma(tr, period)

    osc_mode = oscillator.upper().strip()
    if osc_mode == "MFI":
        if volume is None:
            raise ValueError("Volume array is required when oscillator='MFI'")
        hlc3 = (h + l + c) / 3.0
        osc = pine_mfi(hlc3, np.asarray(volume, dtype=float), period)
    elif osc_mode == "RSI":
        osc = pine_rsi(c, period)
    else:
        raise ValueError(f"Unsupported oscillator '{oscillator}'. Choose 'MFI' or 'RSI'.")

    up_threshold = l - atr * multiplier
    down_threshold = h + atr * multiplier

    alpha_trend = np.full(n, np.nan, dtype=float)
    for idx in range(n):
        previous = float(alpha_trend[idx - 1]) if idx > 0 and math.isfinite(alpha_trend[idx - 1]) else 0.0
        bullish = math.isfinite(osc[idx]) and osc[idx] >= 50.0
        if bullish:
            cand = float(up_threshold[idx])
            alpha_trend[idx] = previous if cand < previous else cand
        else:
            cand = float(down_threshold[idx])
            alpha_trend[idx] = previous if cand > previous else cand

    # line_2 is the 2-bar lag of AlphaTrend
    line_2 = np.full(n, np.nan, dtype=float)
    if n > 2:
        line_2[2:] = alpha_trend[:-2]

    buy_signal, sell_signal = cross_signals(alpha_trend, line_2)

    return AlphaTrendResult(
        alpha_trend=alpha_trend,
        line_2=line_2,
        up_threshold=up_threshold,
        down_threshold=down_threshold,
        oscillator=osc,
        buy_signal=buy_signal,
        sell_signal=sell_signal,
    )
