"""Example 01: Kivanc Ozbilgic Trend Algorithms Suite.

Demonstrates running AlphaTrend, Optimized Trend Tracker (OTT), and Profit Maximizer (PMax)
on sample OHLCV market data.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numpy as np

from tradingview_indicators import alphatrend, ott, pmax


def main():
    print("=" * 70)
    print("Example 01: Kivanc Ozbilgic Trend Algorithms Suite")
    print("=" * 70)

    # Generate synthetic price series with trend and volatility
    np.random.seed(42)
    n = 60
    prices = 100.0 + np.cumsum(np.random.randn(n) * 0.8)
    high = prices + np.random.uniform(0.5, 1.5, n)
    low = prices - np.random.uniform(0.5, 1.5, n)
    close = prices + np.random.uniform(-0.3, 0.3, n)
    volume = np.random.uniform(500.0, 3000.0, n)

    # 1. AlphaTrend
    res_alpha = alphatrend(high, low, close, volume=volume, period=14, multiplier=1.0)
    print("\n[1] AlphaTrend (period=14, mult=1.0, osc=MFI):")
    print(f"  Final Close       : {close[-1]:.2f}")
    print(f"  AlphaTrend Line   : {res_alpha.alpha_trend[-1]:.2f}")
    print(f"  Line 2 (2-bar lag): {res_alpha.line_2[-1]:.2f}")
    print(f"  MFI Oscillator    : {res_alpha.oscillator[-1]:.2f}")
    print(f"  Total Buy Signals : {np.sum(res_alpha.buy_signal)}")
    print(f"  Total Sell Signals: {np.sum(res_alpha.sell_signal)}")

    # 2. Optimized Trend Tracker (OTT)
    res_ott = ott(close, period=14, percent=1.0, ma_type="VAR")
    print("\n[2] Optimized Trend Tracker (OTT) (period=14, percent=1.0, ma=VAR):")
    print(f"  Variable MA (VIDYA): {res_ott.variable_ma[-1]:.2f}")
    print(f"  Master Trend (MT)  : {res_ott.mt[-1]:.2f}")
    print(f"  OTT Envelope       : {res_ott.ott[-1]:.2f}")
    print(f"  Direction State    : {'BULLISH' if res_ott.direction[-1] == 1 else 'BEARISH'}")
    print(f"  Total Buy Signals  : {np.sum(res_ott.buy_signal)}")
    print(f"  Total Sell Signals : {np.sum(res_ott.sell_signal)}")

    # 3. Profit Maximizer (PMax)
    res_pmax = pmax(high, low, close, ma_length=10, atr_length=10, multiplier=3.0, ma_type="EMA")
    print("\n[3] Profit Maximizer (PMax) (ma=10, atr=10, mult=3.0, ma=EMA):")
    print(f"  Base EMA           : {res_pmax.mavg[-1]:.2f}")
    print(f"  PMax Dynamic Stop  : {res_pmax.pmax[-1]:.2f}")
    print(f"  Direction State    : {'BULLISH' if res_pmax.direction[-1] == 1 else 'BEARISH'}")
    print(f"  Total Buy Signals  : {np.sum(res_pmax.buy_signal)}")
    print(f"  Total Sell Signals : {np.sum(res_pmax.sell_signal)}")


if __name__ == "__main__":
    main()
