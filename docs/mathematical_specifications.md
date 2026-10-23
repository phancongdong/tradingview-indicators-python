# Mathematical Specifications

This document outlines the formal mathematical formulations for the core indicators implemented in `tradingview-indicators-python`.

---

## 1. AlphaTrend (Kıvanç Özbilgiç)

### Dynamic Volatility Band
$$
\text{TR}_t = \max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)
$$
$$
\text{ATR}_t = \text{SMA}(\text{TR}_t, \text{period})
$$
$$
\text{UpThreshold}_t = L_t - \text{ATR}_t \cdot \text{multiplier}
$$
$$
\text{DownThreshold}_t = H_t + \text{ATR}_t \cdot \text{multiplier}
$$

### State Machine Recursion
Given an oscillator $\mathcal{O}_t \in [0, 100]$ (Money Flow Index or Relative Strength Index):

$$
\text{AlphaTrend}_t = \begin{cases}
\max(\text{UpThreshold}_t, \text{AlphaTrend}_{t-1}), & \text{if } \mathcal{O}_t \ge 50 \\
\min(\text{DownThreshold}_t, \text{AlphaTrend}_{t-1}), & \text{if } \mathcal{O}_t < 50
\end{cases}
$$

### Signal Logic
$$
\text{Line2}_t = \text{AlphaTrend}_{t-2}
$$
$$
\text{Buy} = \text{AlphaTrend}_t > \text{Line2}_t \land \text{AlphaTrend}_{t-1} \le \text{Line2}_{t-1}
$$
$$
\text{Sell} = \text{AlphaTrend}_t < \text{Line2}_t \land \text{AlphaTrend}_{t-1} \ge \text{Line2}_{t-1}
$$

---

## 2. Optimized Trend Tracker - OTT (Kıvanç Özbilgiç)

### Adaptive Variable Average
Let $\text{VAR}_t$ be the Variable Index Dynamic Average (VIDYA) of price:
$$
\text{RawLong}_t = \text{VAR}_t \cdot (1 - \text{percent} \cdot 0.01)
$$
$$
\text{RawShort}_t = \text{VAR}_t \cdot (1 + \text{percent} \cdot 0.01)
$$

### Trailing Stop Bands
$$
\text{LongStop}_t = \begin{cases}
\max(\text{RawLong}_t, \text{LongStop}_{t-1}), & \text{if } \text{VAR}_t > \text{LongStop}_{t-1} \\
\text{RawLong}_t, & \text{otherwise}
\end{cases}
$$

$$
\text{ShortStop}_t = \begin{cases}
\min(\text{RawShort}_t, \text{ShortStop}_{t-1}), & \text{if } \text{VAR}_t < \text{ShortStop}_{t-1} \\
\text{RawShort}_t, & \text{otherwise}
\end{cases}
$$

### Master Trend (MT) and OTT Envelope
$$
\text{Direction}_t = \begin{cases}
1, & \text{if } \text{Direction}_{t-1} = -1 \land \text{VAR}_t > \text{ShortStop}_{t-1} \\
-1, & \text{if } \text{Direction}_{t-1} = 1 \land \text{VAR}_t < \text{LongStop}_{t-1} \\
\text{Direction}_{t-1}, & \text{otherwise}
\end{cases}
$$

$$
\text{MT}_t = \begin{cases}
\text{LongStop}_t, & \text{if } \text{Direction}_t = 1 \\
\text{ShortStop}_t, & \text{if } \text{Direction}_t = -1
\end{cases}
$$

$$
\text{OTT}_t = \begin{cases}
\text{MT}_t \cdot \frac{200 + \text{percent}}{200}, & \text{if } \text{VAR}_t > \text{MT}_t \\
\text{MT}_t \cdot \frac{200 - \text{percent}}{200}, & \text{if } \text{VAR}_t \le \text{MT}_t
\end{cases}
$$

---

## 3. Profit Maximizer - PMax (Kıvanç Özbilgiç)

Combines an Exponential Moving Average (or HMA/VAR) $\mu_t$ with an ATR volatility buffer $\sigma_t$:
$$
\text{RawLong}_t = \mu_t - \text{multiplier} \cdot \sigma_t
$$
$$
\text{RawShort}_t = \mu_t + \text{multiplier} \cdot \sigma_t
$$

$$
\text{LongStop}_t = \begin{cases}
\max(\text{RawLong}_t, \text{LongStop}_{t-1}), & \text{if } \mu_t > \text{LongStop}_{t-1} \\
\text{RawLong}_t, & \text{otherwise}
\end{cases}
$$

$$
\text{ShortStop}_t = \begin{cases}
\min(\text{RawShort}_t, \text{ShortStop}_{t-1}), & \text{if } \mu_t < \text{ShortStop}_{t-1} \\
\text{RawShort}_t, & \text{otherwise}
\end{cases}
$$

$$
\text{PMax}_t = \begin{cases}
\text{LongStop}_t, & \text{if } \text{Direction}_t = 1 \\
\text{ShortStop}_t, & \text{if } \text{Direction}_t = -1
\end{cases}
$$

---

## 4. UT Bot Alerts (QuantNomad)

Let $\delta_t = \text{sensitivity} \cdot \text{ATR}_t$:

$$
\text{Stop}_t = \begin{cases}
\max(\text{Stop}_{t-1}, C_t - \delta_t), & \text{if } C_t > \text{Stop}_{t-1} \land C_{t-1} > \text{Stop}_{t-1} \\
\min(\text{Stop}_{t-1}, C_t + \delta_t), & \text{if } C_t < \text{Stop}_{t-1} \land C_{t-1} < \text{Stop}_{t-1} \\
C_t - \delta_t, & \text{if } C_t > \text{Stop}_{t-1} \\
C_t + \delta_t, & \text{if } C_t \le \text{Stop}_{t-1}
\end{cases}
$$

Buy alert triggers on crossover $(C_t > \text{Stop}_t \land C_{t-1} \le \text{Stop}_{t-1})$.
Sell alert triggers on crossunder $(C_t < \text{Stop}_t \land C_{t-1} \ge \text{Stop}_{t-1})$.

---

## 5. WaveTrend Oscillator (LazyBear)

$$
\text{Typical}_t = \frac{H_t + L_t + C_t}{3}
$$
$$
\text{ESA}_t = \text{EMA}(\text{Typical}_t, \text{channel\_length})
$$
$$
\mathcal{D}_t = \text{EMA}(|\text{Typical}_t - \text{ESA}_t|, \text{channel\_length})
$$
$$
\text{CI}_t = \frac{\text{Typical}_t - \text{ESA}_t}{0.015 \cdot \mathcal{D}_t}
$$
$$
\text{WT1}_t = \text{EMA}(\text{CI}_t, \text{average\_length})
$$
$$
\text{WT2}_t = \text{SMA}(\text{WT1}_t, \text{signal\_length})
$$
