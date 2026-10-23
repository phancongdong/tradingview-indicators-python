"""LazyBear's WaveTrend oscillator ported from TradingView Pine Script.

WaveTrend applies exponential smoothing to a normalized commodity channel index (CCI),
producing clean, responsive overbought and oversold cycle turning points.
"""
from __future__ import annotations

import numpy as np

from tradingview_indicators.core.math import cross_signals, pine_ema, pine_sma
from tradingview_indicators.core.types import WaveTrendResult


def wavetrend(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    channel_length: int = 10,
    average_length: int = 21,
    signal_length: int = 4,
    oversold_threshold: float = -53.0,
    overbought_threshold: float = 53.0,
) -> WaveTrendResult:
    """Compute LazyBear's WaveTrend oscillator.

    Parameters:
        high: High price series.
        low: Low price series.
        close: Close price series.
        channel_length: Channel EMA lookback window (default: 10).
        average_length: Normalized oscillator smoothing EMA window (default: 21).
        signal_length: Signal line SMA window (default: 4).
        oversold_threshold: Threshold below which bullish crosses trigger (default: -53.0).
        overbought_threshold: Threshold above which bearish crosses trigger (default: 53.0).

    Returns:
        WaveTrendResult with wt1 (main oscillator), wt2 (signal line), and cross masks.
    """
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    c = np.asarray(close, dtype=float)

    typical = (h + l + c) / 3.0
    esa = pine_ema(typical, channel_length)
    deviation = pine_ema(np.abs(typical - esa), channel_length)

    dev_safe = np.where(deviation == 0.0, np.nan, deviation)
    channel_index = (typical - esa) / (0.015 * dev_safe)

    wt1 = pine_ema(channel_index, average_length)
    wt2 = pine_sma(wt1, signal_length)

    cross_up, cross_down = cross_signals(wt1, wt2)
    bullish_cross = cross_up & (wt2 <= oversold_threshold)
    bearish_cross = cross_down & (wt2 >= overbought_threshold)

    return WaveTrendResult(
        wt1=wt1,
        wt2=wt2,
        bullish_cross=bullish_cross,
        bearish_cross=bearish_cross,
    )
