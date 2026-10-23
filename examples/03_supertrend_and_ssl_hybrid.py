"""Example 03: SuperTrend & SSL Hybrid Dynamic Channels.

Demonstrates computing Olivier Seban's canonical SuperTrend alongside Mihkel00's
SSL Hybrid channel for trend filtering.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numpy as np

from tradingview_indicators import ssl_hybrid, supertrend


def main():
    print("=" * 70)
    print("Example 03: SuperTrend & SSL Hybrid Channels")
    print("=" * 70)

    np.random.seed(99)
    n = 50
    base = np.linspace(50.0, 70.0, n) + np.random.randn(n) * 0.5
    high = base + np.random.uniform(0.5, 1.2, n)
    low = base - np.random.uniform(0.5, 1.2, n)
    close = base + np.random.uniform(-0.3, 0.3, n)

    st_res = supertrend(high, low, close, period=10, factor=3.0)
    ssl_res = ssl_hybrid(high, low, close, ssl_length=10, ma_type="HMA")

    print("\nRecent 10 Bars:")
    print(f"{'Bar':<5} | {'Close':<8} | {'SuperTrend':<10} | {'ST Bias':<8} | {'SSL Band':<10} | {'SSL Bias'}")
    print("-" * 65)

    for i in range(n - 10, n):
        st_bias = "BULL" if st_res.direction[i] == 1 else "BEAR"
        ssl_bias = "BULL" if ssl_res.hlv[i] == 1 else "BEAR"
        print(
            f"{i:<5} | {close[i]:<8.2f} | {st_res.supertrend[i]:<10.2f} | "
            f"{st_bias:<8} | {ssl_res.ssl_down[i]:<10.2f} | {ssl_bias}"
        )


if __name__ == "__main__":
    main()
