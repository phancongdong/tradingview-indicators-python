# Pine Script Compatibility & Quirks

When translating Pine Script algorithms from TradingView to Python, subtle differences in built-in mathematical implementations often cause divergence if not carefully handled. This document details the key mathematical quirks replicated in `tradingview-indicators-python`.

---

## 1. Wilder's Moving Average: `ta.rma` vs `ta.ema`

Pine Script provides two distinct exponential smoothing functions:
- `ta.ema(source, length)`: Uses exponential smoothing factor $\alpha = \frac{2}{\text{length} + 1}$.
- `ta.rma(source, length)`: Uses Wilder's smoothing factor $\alpha = \frac{1}{\text{length}}$.

### The RMA Seeding Quirk
In standard exponential moving averages, the recursion is often seeded with the very first observation ($y_0 = x_0$). However, Pine Script's `ta.rma` accumulates the first `length` finite observations and initializes the recursion with their **exact arithmetic mean**:

$$
\text{Seed} = \frac{1}{\text{length}} \sum_{i=0}^{\text{length}-1} x_i
$$

For subsequent bars $t \ge \text{length}$:

$$
y_t = \alpha \cdot x_t + (1 - \alpha) \cdot y_{t-1}, \quad \text{where } \alpha = \frac{1}{\text{length}}
$$

Failure to replicate this seeding mechanism leads to persistent errors that decay slowly over hundreds of bars.

---

## 2. Hull Moving Average (HMA) Root Rounding

TradingView computes `ta.hma(source, length)` using the formula:

$$
\text{HMA}(n) = \text{WMA}\left(2 \cdot \text{WMA}(n/2) - \text{WMA}(n), \lfloor \sqrt{n} + 0.5 \rfloor\right)
$$

Key details:
- $n/2$ is truncated to integer via integer division (`length // 2`).
- The outer smoothing length $\sqrt{n}$ is rounded to the nearest integer using `floor(sqrt(n) + 0.5)` with a minimum clamp of 1.

---

## 3. Variable Index Dynamic Average (VIDYA / VAR MA)

Used prominently in Kıvanç Özbilgiç's OTT, PMax, and VAR indicators. The weighting factor adapts dynamically based on the 9-period Chande Momentum Oscillator (CMO):

$$
\text{CMO}_t = \frac{\sum_{i=0}^8 \max(\Delta P_t, 0) - \sum_{i=0}^8 \max(-\Delta P_t, 0)}{\sum_{i=0}^8 |\Delta P_t|}
$$

$$
\alpha_{\text{base}} = \frac{2}{\text{length} + 1}
$$

$$
k_t = \alpha_{\text{base}} \cdot |\text{CMO}_t|
$$

$$
\text{VAR}_t = k_t \cdot P_t + (1 - k_t) \cdot \text{VAR}_{t-1}
$$

---

## 4. `nz()` Initial Condition Handling

In Pine Script, accessing uninitialized series indices (e.g. `AlphaTrend[1]` at bar 0) returns `NaN`. Pine scripts universally wrap historical references in `nz(val, replacement)`:
- `nz(x)` evaluates to `0.0` if `x` is NaN or uninitialized.
- In `tradingview-indicators-python`, state machines mirror this by maintaining explicit fallback values ($0.0$) on initial bars rather than propagating NaNs into the recursive accumulator.

---

## 5. Strict Point-In-Time Causality

TradingView indicators evaluated in Pine Script execute sequentially from bar `0` to bar `n-1`. At bar $t$, only data from bars $0 \dots t$ are available.
All functions in `tradingview-indicators-python` guarantee strict point-in-time causality:
- No forward-looking rolling windows (`center=True` is never used).
- No future index leakage.
- Bar $t$ calculations depend exclusively on historical closed bar attributes.
