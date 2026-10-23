"""Example 04: WaveTrend, Connors RSI, and Fisher Transform Oscillators.

Demonstrates computing leading turning-point oscillators commonly used in Pine Script.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numpy as np

from tradingview_indicators import connors_rsi, fisher_transform, wavetrend


def main():
    print("=" * 70)
    print("Example 04: WaveTrend, Connors RSI, and Fisher Transform")
    print("=" * 70)

    np.random.seed(55)
    n = 60
    base = 100.0 + np.sin(np.linspace(0, 4 * np.pi, n)) * 10.0
    high = base + np.random.uniform(0.5, 1.5, n)
    low = base - np.random.uniform(0.5, 1.5, n)
    close = base + np.random.uniform(-0.2, 0.2, n)

    wt = wavetrend(high, low, close)
    crsi = connors_rsi(close, rsi_period=3, streak_period=2, rank_period=20)
    fish = fisher_transform(high, low, period=10)

    print("\nRecent 10 Oscillator Readings:")
    print(f"{'Bar':<5} | {'Close':<8} | {'WaveTrend wt1':<14} | {'Connors RSI':<12} | {'Fisher Transform':<16}")
    print("-" * 65)

    for i in range(n - 10, n):
        print(
            f"{i:<5} | {close[i]:<8.2f} | {wt.wt1[i]:<14.2f} | "
            f"{crsi.crsi[i]:<12.2f} | {fish.fisher[i]:<16.2f}"
        )


if __name__ == "__main__":
    main()
