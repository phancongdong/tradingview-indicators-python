"""Example 02: QuantNomad's UT Bot Alerts Dynamic Trailing Stop.

Demonstrates tracking market price with UT Bot's ATR-based trailing stop and detecting
clean buy/sell breakout events.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numpy as np

from tradingview_indicators import ut_bot


def main():
    print("=" * 70)
    print("Example 02: QuantNomad's UT Bot Alerts")
    print("=" * 70)

    # Simulate an uptrend followed by a reversal
    np.random.seed(101)
    n = 40
    trend = np.concatenate([np.linspace(100.0, 120.0, 25), np.linspace(120.0, 105.0, 15)])
    close = trend + np.random.normal(0, 0.4, n)
    high = close + np.random.uniform(0.3, 1.0, n)
    low = close - np.random.uniform(0.3, 1.0, n)

    res = ut_bot(close, high, low, sensitivity=1.5, atr_period=10)

    print(f"{'Bar':<5} | {'Close':<8} | {'UT Stop':<8} | {'Position':<10} | {'Signal'}")
    print("-" * 50)

    for i in range(15, n):
        sig = ""
        if res.buy_signal[i]:
            sig = "BUY ALERT"
        elif res.sell_signal[i]:
            sig = "SELL ALERT"
        pos = "ABOVE STOP" if close[i] > res.stop[i] else "BELOW STOP"
        print(f"{i:<5} | {close[i]:<8.2f} | {res.stop[i]:<8.2f} | {pos:<10} | {sig}")


if __name__ == "__main__":
    main()
