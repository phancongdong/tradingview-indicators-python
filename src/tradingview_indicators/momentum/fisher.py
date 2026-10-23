"""John Ehlers' Fisher Transform oscillator ported from Pine Script.

Transforms financial asset prices into a Gaussian normal distribution with sharp,
distinct turning points and zero-lag pivot characteristics.
"""
from __future__ import annotations

import math
import numpy as np
import pandas as pd

from tradingview_indicators.core.types import FisherResult


def fisher_transform(
    high: np.ndarray,
    low: np.ndarray,
    period: int = 10,
) -> FisherResult:
    """Compute Ehlers Fisher Transform.

    Parameters:
        high: High price series.
        low: Low price series.
        period: Lookback window for min/max price normalization (default: 10).

    Returns:
        FisherResult containing the fisher series and its 1-bar trigger line.
    """
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    n = len(h)

    price = (h + l) / 2.0
    rolling_low = pd.Series(price).rolling(period, min_periods=period).min().to_numpy(dtype=float)
    rolling_high = pd.Series(price).rolling(period, min_periods=period).max().to_numpy(dtype=float)

    fisher = np.full(n, np.nan, dtype=float)
    prev_val = 0.0
    prev_fish = 0.0

    for idx in range(n):
        curr_price = price[idx]
        min_p = rolling_low[idx]
        max_p = rolling_high[idx]

        if not (math.isfinite(curr_price) and math.isfinite(min_p) and math.isfinite(max_p)):
            continue

        scale = max_p - min_p
        raw = 0.66 * ((curr_price - min_p) / scale - 0.5) if scale > 0.0 else 0.0
        val = float(np.clip(raw + 0.67 * prev_val, -0.999, 0.999))
        fish = 0.5 * math.log((1.0 + val) / (1.0 - val)) + 0.5 * prev_fish

        fisher[idx] = fish
        prev_val = val
        prev_fish = fish

    trigger = np.full(n, np.nan, dtype=float)
    if n > 1:
        trigger[1:] = fisher[:-1]

    return FisherResult(
        fisher=fisher,
        trigger=trigger,
    )
