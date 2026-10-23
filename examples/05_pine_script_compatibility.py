"""Example 05: Pine Script Internal Compatibility and Smoothing Nuances.

Demonstrates the mathematical differences between:
1. Standard Exponential Moving Average (EMA)
2. Wilder's Moving Average / Pine RMA (ta.rma)
3. Simple Moving Average (SMA)
4. Variable Dynamic Moving Average (VIDYA / VAR MA)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numpy as np

from tradingview_indicators import pine_ema, pine_rma, pine_sma, var_ma


def main():
    print("=" * 70)
    print("Example 05: Pine Script Internal Smoothing Compatibility")
    print("=" * 70)

    # Step impulse response: constant 10 then jump to 20
    data = np.array([10.0] * 10 + [20.0] * 10)
    period = 5

    sma = pine_sma(data, period)
    ema = pine_ema(data, period)
    rma = pine_rma(data, period)
    var = var_ma(data, period)

    print(f"\nStep Function Response (Period = {period}):")
    print(f"{'Bar':<5} | {'Raw':<5} | {'Pine SMA':<9} | {'Pine EMA':<9} | {'Pine RMA':<9} | {'VAR MA':<9}")
    print("-" * 55)

    for i in range(8, len(data)):
        print(
            f"{i:<5} | {data[i]:<5.1f} | {sma[i]:<9.2f} | {ema[i]:<9.2f} | {rma[i]:<9.2f} | {var[i]:<9.2f}"
        )

    print("\nKey Takeaways:")
    print("1. Pine EMA alpha = 2 / (N + 1) = 2/6 = 0.333. Reacts fastest to impulse.")
    print("2. Pine RMA alpha = 1 / N = 1/5 = 0.200. Smoother Wilder decay matching ta.rma.")
    print("3. VAR MA dynamically weights based on Chande Momentum Oscillator.")


if __name__ == "__main__":
    main()
