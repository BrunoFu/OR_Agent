---
layout: page
title: Dataset
permalink: /dataset
---

# Dataset

The **AI Agents for Inventory Control Benchmark** consists of 1,320 instances split between synthetic trajectories and real demand trajectories. Each instance defines a single multi‑period inventory game.

[Download from Hugging Face](https://huggingface.co/datasets/Yaopeng12138/inventory_control_benchmark_instances){:.hero-button .primary target="_blank" rel="noopener"} [Benchmark code](https://github.com/BrunoFu/OR_Agent){:.hero-button target="_blank" rel="noopener"}

## Instance families

### Synthetic trajectories (720 instances)

Synthetically generated demand trajectories covering 10 distinct demand patterns, each with 4 parameter variants.

- 10 patterns × 4 variants = **40 distributions**
- 2 demand realizations × 3 profit‑to‑holding‑cost ratios = **6 instances per variant**
- 3 lead‑time settings
- **Total: 40 × 6 × 3 = 720 instances**

### Real trajectories (600 instances)

Weekly sales data from H&M retail, covering 200 distinct product articles.

- 200 articles
- 3 lead‑time settings
- Random profit‑to‑holding‑cost ratios
- **Total: 200 × 3 = 600 instances**

## Directory layout

On Hugging Face, the benchmark is organized as:

```text
inventory_control_benchmark_instances/
├── synthetic_trajectory/
│   ├── lead_time_0/
│   ├── lead_time_4/
│   └── lead_time_stochastic/
└── real_trajectory/
    ├── lead_time_0/
    ├── lead_time_4/
    └── lead_time_stochastic/
```

Each leaf directory contains multiple instance folders. For example:

```text
synthetic_trajectory/lead_time_0/p01_stationary_iid/v1_normal_100_25/r1_low/
  train.csv
  test.csv
```

```text
real_trajectory/lead_time_0/108775044/
  train.csv
  test.csv
```

## File formats

Each instance directory contains:

| File | Description |
|------|-------------|
| `train.csv` | Historical demand samples (context for algorithms) |
| `test.csv`  | Demand trajectory for evaluation |

### <code>train.csv</code>

```csv
exact_dates_{item_id},demand_{item_id}
Period_1,108
Period_2,124
...
```

- **Synthetic**: five samples from the underlying distribution.
- **Real**: five weekly observations preceding the test period (actual dates in `YYYY-MM-DD` format).

### <code>test.csv</code>

```csv
exact_dates_{item_id},demand_{item_id},lead_time_{item_id},profit_{item_id},holding_cost_{item_id}
Period_1,108,0,4,1
Period_2,124,0,4,1
...
```

Columns:

- `exact_dates`: period identifier (synthetic) or actual date (real).
- `demand`: realized demand.
- `lead_time`: order lead time (e.g., 0, 4, or stochastic values).
- `profit`: profit per unit sold.
- `holding_cost`: holding cost per unit per period.

## Lead times

We provide three lead‑time configurations:

- **`lead_time_0`**: immediate delivery (no delay).
- **`lead_time_4`**: fixed four‑period delay.
- **`lead_time_stochastic`**: per‑order lead times drawn from a small discrete set, including values that represent never‑arriving orders.

The same stochastic lead‑time sequence is shared across instances within each family to support fair comparisons.

## Cost structures

Three profit‑to‑holding‑cost ratios are used:

- **Low**: 1:1 (balanced stockout vs holding costs).
- **Medium**: 4:1 (moderate stockout penalty).
- **High**: 19:1 (high stockout penalty for service‑critical items).

Synthetic instances cycle systematically through these ratios; real instances sample them randomly.

## Using the dataset

- Download the full dataset from Hugging Face.
- Use the directory and file naming scheme to iterate over instances.
- For reference implementations and loaders, see the [benchmark code repository](https://github.com/BrunoFu/OR_Agent).

