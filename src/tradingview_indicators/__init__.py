"""TradingView Indicators in Python.

A collection of popular TradingView Pine Script indicators and quantitative algorithms
ported to native, causal, high-performance Python and NumPy.
"""
from __future__ import annotations

# Core Math & Primitives
from tradingview_indicators.core.math import (
    cross_signals,
    crossed_over,
    crossed_under,
    moving_average,
    pine_ema,
    pine_hma,
    pine_rma,
    pine_rsi,
    pine_sma,
    pine_wma,
    true_range,
    var_ma,
    wilder_atr,
    zlema,
)

# Core Output Types
from tradingview_indicators.core.types import (
    AlphaTrendResult,
    AroonResult,
    ConnorsRSIResult,
    ElderImpulseResult,
    FisherResult,
    KAMAResult,
    OTTResult,
    PMaxResult,
    SSLHybridResult,
    SuperTrendResult,
    UTBotResult,
    VortexResult,
    WaveTrendResult,
)

# Trend Indicators
from tradingview_indicators.trend.alphatrend import alphatrend
from tradingview_indicators.trend.ott import ott
from tradingview_indicators.trend.pmax import pmax
from tradingview_indicators.trend.supertrend import supertrend

# Breakout & Trailing Stop Systems
from tradingview_indicators.breakout.ssl_hybrid import ssl_hybrid
from tradingview_indicators.breakout.ut_bot import ut_bot

# Momentum & Oscillators
from tradingview_indicators.momentum.aroon import aroon
from tradingview_indicators.momentum.connors_rsi import connors_rsi
from tradingview_indicators.momentum.elder_impulse import elder_impulse
from tradingview_indicators.momentum.fisher import fisher_transform
from tradingview_indicators.momentum.kama import kama
from tradingview_indicators.momentum.vortex import vortex
from tradingview_indicators.momentum.wavetrend import wavetrend

__version__ = "0.1.0"

__all__ = [
    # Math Primitives
    "pine_sma",
    "pine_ema",
    "pine_rma",
    "pine_wma",
    "pine_hma",
    "var_ma",
    "zlema",
    "moving_average",
    "true_range",
    "wilder_atr",
    "pine_rsi",
    "cross_signals",
    "crossed_over",
    "crossed_under",
    # Indicators
    "alphatrend",
    "ott",
    "pmax",
    "supertrend",
    "ut_bot",
    "ssl_hybrid",
    "wavetrend",
    "connors_rsi",
    "vortex",
    "aroon",
    "fisher_transform",
    "kama",
    "elder_impulse",
    # Dataclasses
    "AlphaTrendResult",
    "OTTResult",
    "PMaxResult",
    "SuperTrendResult",
    "UTBotResult",
    "SSLHybridResult",
    "WaveTrendResult",
    "VortexResult",
    "AroonResult",
    "FisherResult",
    "ConnorsRSIResult",
    "KAMAResult",
    "ElderImpulseResult",
]
