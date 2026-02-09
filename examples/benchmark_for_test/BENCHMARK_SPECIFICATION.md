# Inventory Management Benchmark Specification

## Overview

This benchmark evaluates inventory management algorithms on demand forecasting and ordering decisions. It consists of two complementary datasets:

| Dataset | Instances | Source | Purpose |
|---------|-----------|--------|---------|
| **Synthetic** | 720 | Generated | Controlled evaluation across diverse demand patterns |
| **Real** | 600 | H&M Sales | Real-world performance validation |

**Total: 1,320 benchmark instances**

---

## Dataset Summary

### Synthetic Data (720 instances)

Synthetically generated demand trajectories covering 10 distinct demand patterns, each with 4 parameter variants.

**Structure:**
- 10 demand patterns × 4 variants = **40 distributions**
- 2 demand realizations × 3 profit-to-holding-cost ratios = **6 instances per variant**
- 3 lead time settings
- **Total: 40 × 6 × 3 = 720 instances**

### Real Data (600 instances)

Weekly sales data from H&M retail, covering 200 distinct product articles.

**Structure:**
- 200 articles
- 3 lead time settings
- Random profit-to-holding-cost ratios
- **Total: 200 × 3 = 600 instances**

---

## Instance Structure

Each instance is a directory containing two CSV files:

| File | Description |
|------|-------------|
| `train.csv` | Historical demand samples (context for algorithms) |
| `test.csv` | Demand trajectory for evaluation (50 periods for synthetic, 48 periods for real) |

### train.csv Format

```csv
exact_dates_{item_id},demand_{item_id}
Period_1,108
Period_2,124
...
```

- **Synthetic**: 5 samples from the underlying distribution
- **Real**: 5 weekly observations preceding the test period (actual dates in YYYY-MM-DD format)

### test.csv Format

```csv
exact_dates_{item_id},demand_{item_id},lead_time_{item_id},profit_{item_id},holding_cost_{item_id}
Period_1,108,0,4,1
Period_2,124,0,4,1
...
```

Columns:
- `exact_dates`: Period identifier (synthetic) or actual date (real)
- `demand`: Actual demand for the period
- `lead_time`: Order lead time (0, 4, or stochastic values)
- `profit`: Profit per unit sold
- `holding_cost`: Holding cost per unit per period

---

## Lead Time Settings

Both datasets include three lead time configurations:

| Setting | Value | Description |
|---------|-------|-------------|
| `lead_time_0` | L = 0 | Immediate delivery (no delay) |
| `lead_time_4` | L = 4 | Fixed 4-period lead time |
| `lead_time_stochastic` | L ∈ {1, 2, 3, inf} | Uniformly sampled each period; "inf" means order never arrives |

**Note**: For stochastic lead time, the same random sequence is used across all instances within each dataset to ensure comparability.

---

## Profit-to-Holding-Cost Ratios

Three P:H ratio configurations are used to evaluate algorithms under different cost structures:

| Name | Profit | Holding Cost | Ratio | Interpretation |
|------|--------|--------------|-------|----------------|
| **Low** | 1 | 1 | 1:1 | Equal cost of stockout vs holding |
| **Medium** | 4 | 1 | 4:1 | Moderate stockout penalty |
| **High** | 19 | 1 | 19:1 | High stockout penalty (service-critical) |

### Application

- **Synthetic**: Each variant has 2 realizations × 3 P:H ratios = 6 instances. The naming convention is `r1_low`, `r1_med`, `r1_high`, `r2_low`, `r2_med`, `r2_high`.
- **Real**: Each of the 600 instances is independently assigned a random P:H ratio from {low, med, high}.

---

## Directory Structure

```
benchmark/
├── synthetic_trajectory/
│   ├── lead_time_0/
│   │   ├── p01_stationary_iid/
│   │   │   ├── v1_normal_100_25/
│   │   │   │   ├── r1_low/  (train.csv, test.csv)
│   │   │   │   ├── r1_med/  (train.csv, test.csv)
│   │   │   │   ├── r1_high/ (train.csv, test.csv)
│   │   │   │   ├── r2_low/  (train.csv, test.csv)
│   │   │   │   ├── r2_med/  (train.csv, test.csv)
│   │   │   │   └── r2_high/ (train.csv, test.csv)
│   │   │   ├── v2_normal_100_40/
│   │   │   │   └── ...
│   │   │   └── ...
│   │   ├── p02_mean_increase/
│   │   └── ...
│   ├── lead_time_4/
│   └── lead_time_stochastic/
│
└── real_trajectory/
    ├── lead_time_0/
    │   ├── 108775044/  (train.csv, test.csv)
    │   ├── 111586001/  (train.csv, test.csv)
    │   └── ... (200 articles total)
    ├── lead_time_4/
    └── lead_time_stochastic/
```

---

## Synthetic Data: Demand Pattern Specifications

### Fixed Parameters

| Parameter | Value |
|-----------|-------|
| Test periods | 50 |
| Train samples | 5 |
| Changepoint location | Period 16 (for single changepoint patterns) |
| AR(1) initial value D₀ | 100 |
| Random seed | 42 |

### Pattern 1: Stationary IID (p01)

Constant distribution throughout all periods.

| Variant | Distribution | Parameters |
|---------|--------------|------------|
| v1 | Normal | μ = 100, σ = 25 |
| v2 | Normal | μ = 100, σ = 40 |
| v3 | Normal | μ = 100, σ = 15 |
| v4 | Uniform | a = 50, b = 150 |

### Pattern 2: Mean Increase at t=16 (p02)

Sudden increase in mean demand at period 16.

| Variant | Before (t ≤ 15) | After (t ≥ 16) | Change |
|---------|-----------------|----------------|--------|
| v1 | N(100, 25) | N(200, 35) | +100% mean |
| v2 | N(100, 25) | N(150, 30) | +50% mean |
| v3 | N(100, 25) | N(300, 50) | +200% mean |
| v4 | N(100, 25) | N(200, 25) | +100% mean, same σ |

### Pattern 3: Mean Decrease at t=16 (p03)

Sudden decrease in mean demand at period 16.

| Variant | Before (t ≤ 15) | After (t ≥ 16) | Change |
|---------|-----------------|----------------|--------|
| v1 | N(100, 25) | N(50, 18) | -50% mean |
| v2 | N(100, 25) | N(70, 20) | -30% mean |
| v3 | N(100, 25) | N(30, 15) | -70% mean |
| v4 | N(150, 30) | N(80, 22) | -47% mean |

### Pattern 4: Increasing Trend (p04)

Gradual increase in demand over time.

| Variant | Mean Function μ(t) | Std Function σ(t) |
|---------|-------------------|-------------------|
| v1 | 100t | 25√t |
| v2 | 50 + 3t | 20 |
| v3 | 100 × 1.05^t | 25 |
| v4 | 100 + 2t | 25√t |

### Pattern 5: Decreasing Trend (p05)

Gradual decrease in demand over time.

| Variant | Mean Function μ(t) | Std Function σ(t) |
|---------|-------------------|-------------------|
| v1 | max(200 - 3t, 50) | 25 |
| v2 | 200 × 0.97^t | 20 |
| v3 | max(150 - 2t, 30) | 20 |
| v4 | 200 / √t | 15 |

### Pattern 6: Variance Change at t=16 (p06)

Change in demand variability at period 16 (mean may remain constant).

| Variant | Before (t ≤ 15) | After (t ≥ 16) | Change |
|---------|-----------------|----------------|--------|
| v1 | N(100, 25) | Uniform[0, 200] | Normal → Uniform |
| v2 | N(100, 25) | N(100, 50) | σ doubles |
| v3 | N(100, 50) | N(100, 20) | σ decreases |
| v4 | Uniform[50, 150] | N(100, 15) | Uniform → Normal |

### Pattern 7: Seasonal/Cyclical (p07)

Periodic demand patterns with sinusoidal variation.

| Variant | Mean Function μ(t) | Period | Amplitude |
|---------|-------------------|--------|-----------|
| v1 | 100 + 30·sin(2πt/10) | 10 | 30 |
| v2 | 100 + 50·sin(2πt/5) | 5 | 50 |
| v3 | 100 + 40·sin(2πt/25) | 25 | 40 |
| v4 | 100 × (1 + 0.3·sin(2πt/10)) | 10 | 30% multiplicative |

All variants use σ = 25.

### Pattern 8: Multiple Changepoints (p08)

Two changepoints creating three distinct demand regimes.

| Variant | t ∈ [1,15] | t ∈ [16,35] | t ∈ [36,50] | Pattern |
|---------|------------|-------------|-------------|---------|
| v1 | N(100, 25) | N(150, 30) | N(80, 20) | Up then down |
| v2 | N(100, 25) | N(60, 20) | N(140, 30) | Down then up |
| v3 | N(100, 25) | N(100, 50) | N(100, 20) | Variance only |
| v4 | N(80, 20) | N(120, 25) | N(100, 22) | Mild fluctuation |

### Pattern 9: Temporary Spike/Dip (p09)

Temporary demand anomaly followed by return to baseline.

| Variant | t ∈ [1,15] | t ∈ [16,25] | t ∈ [26,50] | Pattern |
|---------|------------|-------------|-------------|---------|
| v1 | N(100, 25) | N(200, 35) | N(100, 25) | Temporary surge |
| v2 | N(100, 25) | N(50, 18) | N(100, 25) | Temporary dip |
| v3 | N(100, 25) | N(250, 40) | N(120, 28) | Surge → new normal |
| v4 | N(100, 25) | N(40, 15) | N(80, 22) | Dip → partial recovery |

### Pattern 10: Autocorrelated AR(1) (p10)

Demand follows an AR(1) process: D_t = φ·D_{t-1} + c + ε, where ε ~ N(0, σ)

Long-run mean = c / (1 - φ) = 100 for all variants.

| Variant | φ (autocorrelation) | c | σ | Behavior |
|---------|---------------------|---|---|----------|
| v1 | 0.7 | 30 | 20 | Strong positive |
| v2 | 0.5 | 50 | 25 | Moderate positive |
| v3 | 0.3 | 70 | 30 | Weak positive |
| v4 | -0.3 | 130 | 25 | Negative (alternating) |

---

## Synthetic Data: Generation Procedure

### Test Data Generation

For each period t = 1, 2, ..., 50:

1. **Normal distribution**: D_t ~ N(μ(t), σ(t)), then truncate at 0 and round
2. **Uniform distribution**: D_t ~ Uniform[a, b], then truncate at 0 and round
3. **AR(1) process**: D_t = φ·D_{t-1} + c + ε where ε ~ N(0, σ), D₀ = 100
4. **Changepoint**: Apply the appropriate segment's distribution based on t

**Post-processing**: D_t = max(0, round(D_t))

### Train Data Generation

The train data generation strategy depends on the pattern type:

| Pattern Type | Train Generation Method |
|--------------|------------------------|
| Stationary (p01) | 5 i.i.d. samples from the distribution |
| Changepoint (p02, p03, p06) | 5 i.i.d. samples from the **first segment** only |
| Multi-changepoint (p08) | 5 i.i.d. samples from the **first segment** only |
| Temp spike/dip (p09) | 5 i.i.d. samples from the **first segment** only |
| Trend (p04, p05) | Sequential samples at t = 1, 2, 3, 4, 5 |
| Seasonal (p07) | Sequential samples at t = 1, 2, 3, 4, 5 |
| AR(1) (p10) | Sequential samples at t = 1, 2, 3, 4, 5 with D₀ = 100 |

**Key property**: For each distribution (pattern × variant), the realizations with the same index (r1_* or r2_*) share **identical train data and demand trajectory**. Only the P:H ratio differs.

### Reproducibility

- Base random seed: 42
- Train seed per distribution: `hash((42, pattern, variant, "train")) % 2^32`
- Test seed per realization: `hash((42, pattern, variant, realization_index)) % 2^32`

---

## Real Data: Source and Processing

### Data Source

- **Origin**: H&M Group retail sales data
- **Granularity**: Weekly aggregated sales
- **Selection**: Top 200 articles by total sales volume in 2019

### Time Period

- **Training period**: 5 weeks (e.g., 2019-01-07 to 2019-02-04)
- **Test period**: 48 weeks (e.g., 2019-02-11 to 2019-12-30)

### Data Processing

1. Weekly sales aggregated from transaction data
2. Articles selected based on sufficient sales history
3. Train/test split at a fixed date across all articles
4. Lead time variations created by copying and modifying the lead_time column
5. P:H ratios randomly assigned (seed=42) to each of the 600 instances

---

## Summary Statistics

### Synthetic Data

| Metric | Value |
|--------|-------|
| Total distributions | 40 |
| Realizations per variant | 6 (2 demand × 3 P:H) |
| Trajectories per lead time | 240 |
| Lead time settings | 3 |
| **Total instances** | **720** |
| Periods per test trajectory | 50 |
| Samples per train file | 5 |

### Real Data

| Metric | Value |
|--------|-------|
| Total articles | 200 |
| Lead time settings | 3 |
| **Total instances** | **600** |
| Periods per test trajectory | 48 |
| Samples per train file | 5 |

### Combined Benchmark

| Metric | Value |
|--------|-------|
| **Total instances** | **1,320** |
| P:H ratio distribution (synthetic) | Equal (1/3 each) |
| P:H ratio distribution (real) | Random (~1/3 each) |

---

## Evaluation Metric

The primary evaluation metric is **cumulative reward** over the test period:

```
Reward = Σ (profit × units_sold - holding_cost × units_held)
```

Where:
- `units_sold = min(demand, available_inventory)`
- `units_held = inventory_on_hand at end of period`

### Perfect Score Baseline

The theoretical maximum (perfect foresight) is computed as:

```
Perfect Score = Σ (demand × profit_per_unit)
```

This represents the upper bound assuming perfect demand knowledge and infinite supply (no stockouts, no holding costs considered).

**Normalized Reward** = Actual Reward / Perfect Score

This ratio provides a standardized performance measure across instances with different demand scales and cost structures.
