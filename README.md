# tradingview-indicators

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests Passing](https://img.shields.io/badge/tests-29%2F29%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A collection of popular **TradingView Pine Script indicators and quantitative algorithms** ported to high-performance, native Python and NumPy.

Engineered with **exact Pine Script numerical parity** (replicating Wilder's RMA seeding, Hull MA root rounding, and Chande-based VIDYA variable smoothing) and **strict point-in-time causality** (zero future lookahead bias).

---

## 📑 Supported Indicators & Algorithmic Lineage

| Indicator / Algorithm | Original Pine Script Author | Category | Key Characteristics |
| :--- | :--- | :--- | :--- |
| **AlphaTrend** | Kıvanç Özbilgiç (`3wdQu7P3`) | Trend / Volatility | Dynamic ATR bounds + MFI/RSI momentum filter + 2-bar lag line |
| **Optimized Trend Tracker (OTT)** | Kıvanç Özbilgiç (`ycDUERPO`) | Trend Following | Variable Index Dynamic Average (VIDYA) + Master Trend (MT) envelope |
| **Profit Maximizer (PMax)** | Kıvanç Özbilgiç (`v6Ws9H9j`) | Trend / Stop | Moving average baseline + ATR trailing volatility band ratchet |
| **SuperTrend** | Olivier Seban (`ta.supertrend`) | Trend / Trailing | Canonical TradingView ATR trailing ratchet and direction flip |
| **UT Bot Alerts** | QuantNomad (`VKMgZdYr`) | Breakout / Stop | High-probability ATR trailing floor/ceiling breakout alerts |
| **SSL Hybrid** | Mihkel00 (`2it69GUx`) | Channel / Breakout | High-Low Hull MA channel + dynamic trend state machine |
| **WaveTrend Oscillator** | LazyBear | Momentum Cycle | Double-smoothed normalized CCI oscillator for pivot turning points |
| **Connors RSI (CRSI-3)** | Larry Connors | Mean Reversion | Composite 3-component oscillator (Price RSI + Streak RSI + Percent Rank) |
| **Vortex Indicator (VI)** | Botes & Siepman | Trend Strength | VI+ / VI- directional vortex distance normalized by True Range |
| **Ehlers Fisher Transform** | John Ehlers | Gaussian Pivot | Converts asset price distribution into a near-Gaussian normal distribution |
| **Aroon & Aroon Oscillator** | Tushar Chande | Time-to-Extremes | Tracks elapsed bars since 25-period highest highs and lowest lows |
| **Kaufman Adaptive MA (KAMA)** | Perry Kaufman | Adaptive Trend | Adapts smoothing inertia dynamically using market Efficiency Ratio (ER) |
| **Elder Impulse System** | Alexander Elder | Regime Classifier | Three-state color classification via 13 EMA slope and MACD histogram momentum |

---

## 🎯 Key Design Principles

1. **Exact Pine Script Mathematical Parity**:
   Standard EMA formulas divergence from Pine Script because TradingView's `ta.rma` uses Wilder's initialization seed ($\text{mean}(x_{0 \dots N-1})$) with $\alpha = 1/N$. This engine matches Pine Script outputs to machine precision.
2. **Strict Point-In-Time Causality**:
   All indicators execute causal state updates. Bar $t$ is mathematically insulated from bar $t+1 \dots \infty$. Verified with automated causality property tests.
3. **Pure Vectorized NumPy / Pandas**:
   Optimized vector pipelines and low-overhead Python loops for recursive trailing stop states.
4. **Structured Typed Outputs**:
   Returns immutable frozen dataclasses (`AlphaTrendResult`, `OTTResult`, `PMaxResult`, etc.) containing continuous lines, stop series, direction states, and boolean crossover masks.

---

## 🚀 Quickstart

### Installation

```bash
git clone https://github.com/phancongdong/tradingview-indicators-python.git
cd tradingview-indicators-python
pip install -e .
```

### 1. AlphaTrend (Kıvanç Özbilgiç)

```python
import numpy as np
from tradingview_indicators import alphatrend

# High, Low, Close, Volume arrays
res = alphatrend(
    high=high_prices,
    low=low_prices,
    close=close_prices,
    volume=volume_series,
    period=14,
    multiplier=1.0,
    oscillator="MFI"  # or 'RSI'
)

print("AlphaTrend Line   :", res.alpha_trend[-1])
print("Line 2 (Trigger)  :", res.line_2[-1])
print("Buy Signal (Cross):", res.buy_signal[-1])
print("Sell Signal       :", res.sell_signal[-1])
```

### 2. Optimized Trend Tracker (OTT)

```python
from tradingview_indicators import ott

res = ott(
    source=close_prices,
    period=14,
    percent=1.0,
    ma_type="VAR"  # VIDYA / Variable MA
)

print("VIDYA MA Line     :", res.variable_ma[-1])
print("Master Trend (MT) :", res.mt[-1])
print("OTT Envelope      :", res.ott[-1])
print("Trend Bias        :", "BULL" if res.direction[-1] == 1 else "BEAR")
```

### 3. UT Bot Alerts Trailing Stop

```python
from tradingview_indicators import ut_bot

res = ut_bot(
    close=close_prices,
    high=high_prices,
    low=low_prices,
    sensitivity=1.5,
    atr_period=10
)

print("Dynamic Trailing Stop:", res.stop[-1])
print("Buy Alert Triggered  :", res.buy_signal[-1])
```

### 4. WaveTrend Oscillator (LazyBear)

```python
from tradingview_indicators import wavetrend

res = wavetrend(high_prices, low_prices, close_prices)

print("WaveTrend 1 (Fast) :", res.wt1[-1])
print("WaveTrend 2 (Signal):", res.wt2[-1])
print("Oversold Reversal   :", res.bullish_cross[-1])
```

---

## 📐 Mathematical Reference

### AlphaTrend Formulation

$$\text{TR}_t = \max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)$$

$$\text{UpThreshold}_t = L_t - \text{SMA}(\text{TR}_t, \text{period}) \cdot \text{multiplier}$$

$$\text{DownThreshold}_t = H_t + \text{SMA}(\text{TR}_t, \text{period}) \cdot \text{multiplier}$$

$$\text{AlphaTrend}_t = \begin{cases}
\max(\text{UpThreshold}_t, \text{AlphaTrend}_{t-1}), & \text{if } \text{MFI}_t \ge 50 \\
\min(\text{DownThreshold}_t, \text{AlphaTrend}_{t-1}), & \text{if } \text{MFI}_t < 50
\end{cases}$$

$$\text{Line2}_t = \text{AlphaTrend}_{t-2}$$

---

### Optimized Trend Tracker (OTT)

Given a Variable Index Dynamic Average $\text{VAR}_t$:

$$\text{LongStop}_t = \begin{cases}
\max(\text{RawLong}_t, \text{LongStop}_{t-1}), & \text{if } \text{VAR}_t > \text{LongStop}_{t-1} \\
\text{RawLong}_t, & \text{otherwise}
\end{cases}$$

$$\text{ShortStop}_t = \begin{cases}
\min(\text{RawShort}_t, \text{ShortStop}_{t-1}), & \text{if } \text{VAR}_t < \text{ShortStop}_{t-1} \\
\text{RawShort}_t, & \text{otherwise}
\end{cases}$$

$$\text{MT}_t = \text{LongStop}_t \quad (\text{if Bullish}) \quad \text{or} \quad \text{ShortStop}_t \quad (\text{if Bearish})$$

$$\text{OTT}_t = \begin{cases}
\text{MT}_t \cdot \frac{200 + \text{percent}}{200}, & \text{if } \text{VAR}_t > \text{MT}_t \\
\text{MT}_t \cdot \frac{200 - \text{percent}}{200}, & \text{if } \text{VAR}_t \le \text{MT}_t
\end{cases}$$

---

## 📂 Repository Structure

```
tradingview-indicators-python/
├── docs/
│   ├── mathematical_specifications.md  # Equations for all 13 algorithms
│   └── pine_script_quirks.md           # Pine RMA seeding & initial state quirks
├── examples/
│   ├── 01_kivanc_trend_suite.py        # AlphaTrend, OTT, and PMax walkthrough
│   ├── 02_ut_bot_trailing_stop.py      # UT Bot trailing stop price trace
│   ├── 03_supertrend_and_ssl_hybrid.py # SuperTrend & SSL Hybrid channels
│   ├── 04_wavetrend_and_oscillators.py # WaveTrend, Connors RSI, Fisher Transform
│   └── 05_pine_script_compatibility.py # EMA vs RMA vs VAR numerical differences
├── src/
│   └── tradingview_indicators/
│       ├── core/
│       │   ├── math.py                 # pine_rma, pine_ema, pine_hma, zlema, var_ma
│       │   └── types.py                # Dataclasses for output series
│       ├── trend/
│       │   ├── alphatrend.py           # Kıvanç Özbilgiç's AlphaTrend
│       │   ├── ott.py                  # Optimized Trend Tracker
│       │   ├── pmax.py                 # Profit Maximizer
│       │   └── supertrend.py           # Canonical ta.supertrend
│       ├── breakout/
│       │   ├── ssl_hybrid.py           # Mihkel00's SSL Hybrid
│       │   └── ut_bot.py               # QuantNomad's UT Bot Alerts
│       └── momentum/
│           ├── aroon.py                # Aroon Indicator & Oscillator
│           ├── connors_rsi.py          # Larry Connors RSI-3
│           ├── elder_impulse.py        # Alexander Elder Impulse System
│           ├── fisher.py               # Ehlers Fisher Transform
│           ├── kama.py                 # Kaufman Adaptive Moving Average
│           ├── vortex.py               # Vortex Indicator
│           └── wavetrend.py            # LazyBear WaveTrend Oscillator
├── tests/
│   ├── test_breakout.py                # UT Bot & SSL Hybrid tests
│   ├── test_causality.py               # Strict point-in-time prefix invariant tests
│   ├── test_math.py                    # Pine math primitive accuracy tests
│   ├── test_momentum.py                # Oscillators and momentum tests
│   └── test_trend.py                   # AlphaTrend, OTT, PMax, SuperTrend tests
├── LICENSE                             # MIT License
├── pyproject.toml                      # Standard PEP 517/518 build definition
├── requirements.txt                    # Runtime dependencies (numpy, pandas)
└── requirements-dev.txt                # Development dependencies (pytest, pytest-cov)
```

---

## 🧪 Verification & Testing

Execute the comprehensive test suite verifying mathematical accuracy, boundary conditions, and causal invariance:

```bash
pytest tests -v
```

Expected output:
```
============================= test session starts =============================
collected 29 items

tests/test_breakout.py::test_ut_bot PASSED                               [  3%]
tests/test_breakout.py::test_ssl_hybrid PASSED                           [  6%]
tests/test_causality.py::test_alphatrend_causality PASSED                 [ 10%]
tests/test_causality.py::test_ott_causality PASSED                        [ 13%]
tests/test_causality.py::test_supertrend_causality PASSED                 [ 17%]
tests/test_causality.py::test_ut_bot_causality PASSED                     [ 20%]
tests/test_causality.py::test_wavetrend_causality PASSED                  [ 24%]
tests/test_math.py::test_pine_sma PASSED                                 [ 27%]
tests/test_math.py::test_pine_ema PASSED                                 [ 31%]
tests/test_math.py::test_pine_rma PASSED                                 [ 34%]
tests/test_math.py::test_pine_wma PASSED                                 [ 37%]
tests/test_math.py::test_pine_hma PASSED                                 [ 41%]
tests/test_math.py::test_var_ma PASSED                                   [ 44%]
tests/test_math.py::test_zlema PASSED                                    [ 48%]
tests/test_math.py::test_moving_average_dispatcher PASSED                 [ 51%]
tests/test_math.py::test_true_range_and_atr PASSED                        [ 55%]
tests/test_math.py::test_cross_signals PASSED                             [ 58%]
tests/test_math.py::test_pine_rsi PASSED                                 [ 62%]
tests/test_momentum.py::test_wavetrend PASSED                            [ 65%]
tests/test_momentum.py::test_connors_rsi PASSED                          [ 68%]
tests/test_momentum.py::test_vortex PASSED                               [ 72%]
tests/test_momentum.py::test_fisher_transform PASSED                      [ 75%]
tests/test_momentum.py::test_aroon PASSED                                [ 79%]
tests/test_momentum.py::test_kama PASSED                                 [ 82%]
tests/test_momentum.py::test_elder_impulse PASSED                         [ 86%]
tests/test_trend.py::test_alphatrend PASSED                              [ 89%]
tests/test_trend.py::test_ott PASSED                                     [ 93%]
tests/test_trend.py::test_pmax PASSED                                    [ 96%]
tests/test_trend.py::test_supertrend PASSED                              [100%]

============================= 29 passed in 1.30s ==============================
```

---

## 👤 Author

**PHAN CONG DONG**
- GitHub: [@phancongdong](https://github.com/phancongdong)
- Email: phancongdong1234@gmail.com

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
