"""Pine Script mathematical primitives and moving average smoothing functions.

Replicates TradingView's exact internal calculation semantics, including Wilder's RMA
seeding, HMA root-rounding, and recursive variable averages.
"""
from __future__ import annotations

import math
import numpy as np
import pandas as pd


def pine_sma(values: np.ndarray, length: int) -> np.ndarray:
    """TradingView ta.sma: Simple moving average over trailing `length` bars."""
    if length <= 0:
        raise ValueError(f"length must be positive, got {length}")
    series = pd.Series(values, dtype=float)
    return series.rolling(length, min_periods=length).mean().to_numpy(dtype=float)


def pine_ema(values: np.ndarray, length: int) -> np.ndarray:
    """TradingView ta.ema: Exponential moving average with alpha = 2 / (length + 1).

    Seeds with the first finite value in the series.
    """
    if length <= 0:
        raise ValueError(f"length must be positive, got {length}")
    arr = np.asarray(values, dtype=float)
    result = np.full(len(arr), np.nan, dtype=float)
    alpha = 2.0 / (length + 1.0)
    prior = math.nan
    for idx, value in enumerate(arr):
        if not math.isfinite(value):
            continue
        if not math.isfinite(prior):
            prior = float(value)
        else:
            prior = alpha * float(value) + (1.0 - alpha) * prior
        result[idx] = prior
    return result


def pine_rma(values: np.ndarray, length: int) -> np.ndarray:
    """TradingView ta.rma: Wilder's moving average with alpha = 1 / length.

    Initial seed is the exact arithmetic mean of the first `length` finite observations,
    matching Pine Script's exact initialization behavior.
    """
    if length <= 0:
        raise ValueError(f"length must be positive, got {length}")
    arr = np.asarray(values, dtype=float)
    result = np.full(len(arr), np.nan, dtype=float)
    seed: list[float] = []
    prior = math.nan
    alpha = 1.0 / length
    for idx, value in enumerate(arr):
        if not math.isfinite(value):
            continue
        if not math.isfinite(prior):
            seed.append(float(value))
            if len(seed) == length:
                prior = float(np.mean(seed))
                result[idx] = prior
        else:
            prior = alpha * float(value) + (1.0 - alpha) * prior
            result[idx] = prior
    return result


def pine_wma(values: np.ndarray, length: int) -> np.ndarray:
    """TradingView ta.wma: Weighted moving average with linear weights 1..length."""
    if length <= 0:
        raise ValueError(f"length must be positive, got {length}")
    arr = np.asarray(values, dtype=float)
    result = np.full(len(arr), np.nan, dtype=float)
    if len(arr) < length:
        return result
    weights = np.arange(1.0, length + 1.0)
    divisor = float(weights.sum())
    for idx in range(length - 1, len(arr)):
        window = arr[idx - length + 1 : idx + 1]
        if np.isfinite(window).all():
            result[idx] = float(np.dot(window, weights) / divisor)
    return result


def pine_hma(values: np.ndarray, length: int) -> np.ndarray:
    """TradingView ta.hma: Hull Moving Average.

    Formula: WMA(2 * WMA(n/2) - WMA(n), round(sqrt(n)))
    """
    if length <= 0:
        raise ValueError(f"length must be positive, got {length}")
    half_length = max(int(length / 2), 1)
    root_length = max(int(math.floor(math.sqrt(length) + 0.5)), 1)
    wma_half = pine_wma(values, half_length)
    wma_full = pine_wma(values, length)
    diff = 2.0 * wma_half - wma_full
    return pine_wma(diff, root_length)


def var_ma(values: np.ndarray, length: int) -> np.ndarray:
    """Variable Index Dynamic Average (VIDYA / VAR MA) driven by 9-period CMO."""
    if length <= 0:
        raise ValueError(f"length must be positive, got {length}")
    arr = np.asarray(values, dtype=float)
    delta = np.diff(arr, prepend=arr[0])
    up = np.maximum(delta, 0.0)
    down = np.maximum(-delta, 0.0)
    up_sum = pd.Series(up).rolling(9, min_periods=9).sum().to_numpy(dtype=float)
    down_sum = pd.Series(down).rolling(9, min_periods=9).sum().to_numpy(dtype=float)
    denominator = up_sum + down_sum
    cmo = np.divide(
        up_sum - down_sum,
        denominator,
        out=np.zeros(len(arr)),
        where=denominator != 0.0,
    )
    cmo[~np.isfinite(cmo)] = 0.0
    alpha = 2.0 / (length + 1.0)
    result = np.full(len(arr), np.nan, dtype=float)
    prior = 0.0
    for idx in range(len(arr)):
        if not math.isfinite(arr[idx]):
            continue
        weight = alpha * abs(float(cmo[idx]))
        prior = weight * float(arr[idx]) + (1.0 - weight) * prior
        result[idx] = prior
    return result


def zlema(values: np.ndarray, length: int) -> np.ndarray:
    """Zero-Lag Exponential Moving Average (ZLEMA)."""
    if length <= 0:
        raise ValueError(f"length must be positive, got {length}")
    arr = np.asarray(values, dtype=float)
    lag = length // 2 if length % 2 == 0 else (length - 1) // 2
    adjusted = np.full(len(arr), np.nan, dtype=float)
    if lag > 0 and len(arr) > lag:
        adjusted[lag:] = arr[lag:] + (arr[lag:] - arr[:-lag])
    else:
        adjusted[:] = arr[:]
    return pine_ema(adjusted, length)


def moving_average(values: np.ndarray, ma_type: str, length: int) -> np.ndarray:
    """Universal dispatcher for moving average types supported in Pine Script."""
    normalized = ma_type.upper().strip()
    if normalized == "SMA":
        return pine_sma(values, length)
    if normalized == "EMA":
        return pine_ema(values, length)
    if normalized == "RMA":
        return pine_rma(values, length)
    if normalized == "WMA":
        return pine_wma(values, length)
    if normalized == "HMA":
        return pine_hma(values, length)
    if normalized == "VAR" or normalized == "VIDYA":
        return var_ma(values, length)
    if normalized == "ZLEMA":
        return zlema(values, length)
    raise ValueError(f"Unsupported moving average type: {ma_type}. Choose SMA, EMA, RMA, WMA, HMA, VAR, ZLEMA.")


def true_range(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    """TradingView ta.tr: True Range calculation."""
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    c = np.asarray(close, dtype=float)
    result = h - l
    if len(result) > 1:
        prev_close = c[:-1]
        result[1:] = np.maximum.reduce(
            [h[1:] - l[1:], np.abs(h[1:] - prev_close), np.abs(l[1:] - prev_close)]
        )
    return result


def wilder_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
    """TradingView ta.atr: Average True Range (Wilder's RMA of True Range)."""
    tr = true_range(high, low, close)
    return pine_rma(tr, period)


def pine_rsi(source: np.ndarray, length: int = 14) -> np.ndarray:
    """TradingView ta.rsi: Relative Strength Index calculated via Pine RMA."""
    arr = np.asarray(source, dtype=float)
    changes = np.full(len(arr), np.nan, dtype=float)
    changes[1:] = arr[1:] - arr[:-1]
    gains = np.where(np.isnan(changes), np.nan, np.maximum(changes, 0.0))
    losses = np.where(np.isnan(changes), np.nan, np.maximum(-changes, 0.0))
    avg_gain = pine_rma(gains, length)
    avg_loss = pine_rma(losses, length)
    result = np.full(len(arr), np.nan, dtype=float)
    finite = np.isfinite(avg_gain) & np.isfinite(avg_loss)
    result[finite & (avg_gain == 0.0) & (avg_loss == 0.0)] = 50.0
    result[finite & (avg_gain > 0.0) & (avg_loss == 0.0)] = 100.0
    result[finite & (avg_gain == 0.0) & (avg_loss > 0.0)] = 0.0
    regular = finite & (avg_gain > 0.0) & (avg_loss > 0.0)
    result[regular] = 100.0 - 100.0 / (1.0 + avg_gain[regular] / avg_loss[regular])
    return result


def cross_signals(left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """TradingView ta.crossover and ta.crossunder vectorized evaluation.

    Returns:
        (crossover_mask, crossunder_mask) as boolean numpy arrays.
    """
    l = np.asarray(left, dtype=float)
    r = np.asarray(right, dtype=float)
    up = np.zeros(len(l), dtype=bool)
    down = np.zeros(len(l), dtype=bool)
    finite = np.isfinite(l) & np.isfinite(r)
    if len(l) > 1:
        up[1:] = finite[1:] & finite[:-1] & (l[1:] > r[1:]) & (l[:-1] <= r[:-1])
        down[1:] = finite[1:] & finite[:-1] & (l[1:] < r[1:]) & (l[:-1] >= r[:-1])
    return up, down


def crossed_over(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Convenience wrapper for ta.crossover boolean mask."""
    up, _ = cross_signals(left, right)
    return up


def crossed_under(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Convenience wrapper for ta.crossunder boolean mask."""
    _, down = cross_signals(left, right)
    return down
