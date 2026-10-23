"""Core data models and structured return types for TradingView indicators."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class AlphaTrendResult:
    """Output series for Kıvanç Özbilgiç's AlphaTrend indicator."""
    alpha_trend: np.ndarray
    line_2: np.ndarray
    up_threshold: np.ndarray
    down_threshold: np.ndarray
    oscillator: np.ndarray
    buy_signal: np.ndarray
    sell_signal: np.ndarray


@dataclass(frozen=True)
class OTTResult:
    """Output series for Kıvanç Özbilgiç's Optimized Trend Tracker (OTT)."""
    ott: np.ndarray
    mt: np.ndarray
    variable_ma: np.ndarray
    long_stop: np.ndarray
    short_stop: np.ndarray
    direction: np.ndarray
    buy_signal: np.ndarray
    sell_signal: np.ndarray


@dataclass(frozen=True)
class PMaxResult:
    """Output series for Kıvanç Özbilgiç's Profit Maximizer (PMax)."""
    pmax: np.ndarray
    mavg: np.ndarray
    long_stop: np.ndarray
    short_stop: np.ndarray
    direction: np.ndarray
    buy_signal: np.ndarray
    sell_signal: np.ndarray


@dataclass(frozen=True)
class SuperTrendResult:
    """Output series for Olivier Seban's canonical SuperTrend."""
    supertrend: np.ndarray
    direction: np.ndarray
    upper_band: np.ndarray
    lower_band: np.ndarray
    buy_signal: np.ndarray
    sell_signal: np.ndarray


@dataclass(frozen=True)
class UTBotResult:
    """Output series for QuantNomad's UT Bot Alerts trailing stop system."""
    stop: np.ndarray
    buy_signal: np.ndarray
    sell_signal: np.ndarray


@dataclass(frozen=True)
class SSLHybridResult:
    """Output series for Mihkel00's SSL Hybrid channel & baseline."""
    ssl_down: np.ndarray
    hlv: np.ndarray
    ma_high: np.ndarray
    ma_low: np.ndarray
    cross_up: np.ndarray
    cross_down: np.ndarray


@dataclass(frozen=True)
class WaveTrendResult:
    """Output series for LazyBear's WaveTrend oscillator."""
    wt1: np.ndarray
    wt2: np.ndarray
    bullish_cross: np.ndarray
    bearish_cross: np.ndarray


@dataclass(frozen=True)
class VortexResult:
    """Output series for Vortex Indicator (VI+ / VI-)."""
    plus_vi: np.ndarray
    minus_vi: np.ndarray
    oscillator: np.ndarray


@dataclass(frozen=True)
class AroonResult:
    """Output series for Aroon indicator & oscillator."""
    aroon_up: np.ndarray
    aroon_down: np.ndarray
    oscillator: np.ndarray


@dataclass(frozen=True)
class FisherResult:
    """Output series for Ehlers Fisher Transform."""
    fisher: np.ndarray
    trigger: np.ndarray


@dataclass(frozen=True)
class ConnorsRSIResult:
    """Output series for Larry Connors RSI-3 composite indicator."""
    crsi: np.ndarray
    rsi: np.ndarray
    streak_rsi: np.ndarray
    percent_rank: np.ndarray


@dataclass(frozen=True)
class KAMAResult:
    """Output series for Kaufman Adaptive Moving Average."""
    kama: np.ndarray
    efficiency_ratio: np.ndarray


@dataclass(frozen=True)
class ElderImpulseResult:
    """Output series for Elder Impulse System (1 = Bullish/Green, -1 = Bearish/Red, 0 = Neutral/Blue)."""
    state: np.ndarray
    ema: np.ndarray
    macd_hist: np.ndarray
