---
layout: page
title: Leaderboard
permalink: /leaderboard
---

# Leaderboard

This page summarizes performance of OR baselines, LLM policies, and OR–LLM hybrids on the **AI Agents for Inventory Control Benchmark**.

The primary evaluation metric is **cumulative reward** over the test period. We also report **normalized reward**, defined as the ratio between actual reward and a perfect‑foresight upper bound.

## Overall leaderboard (placeholder)

| Rank | Method | LLM | Category | Normalized Reward | Reference |
|------|--------|-----|----------|-------------------|-----------|
| –    | Coming soon | – | – | – | – |

We will populate this table once public baselines are finalized.

## Metric definition

For each instance, cumulative reward is:

```text
Reward = Σ_t (profit_t × units_sold_t − holding_cost_t × units_held_t)
```

where:

- `units_sold_t = min(demand_t, available_inventory_t)`
- `units_held_t` is the end‑of‑period on‑hand inventory.

The **perfect score** assumes perfect knowledge of future demand and unlimited supply:

```text
PerfectScore = Σ_t (demand_t × profit_t)
```

We report **normalized reward** as:

```text
NormalizedReward = Reward / PerfectScore
```

This normalizes performance across instances with different demand scales and cost parameters.

## Sub-leaderboards (planned)

We plan to provide separate tables for:

- **Synthetic trajectories only**
- **Real trajectories only**
- **By lead‑time regime** (for example, `lead_time_0`, `lead_time_4`, `lead_time_stochastic`)

These will reuse the same columns and metric definitions as the overall leaderboard.

## Submitting results (to be finalized)

Once the submission pipeline is ready, we will:

- Specify a standard result file format (for example, CSV or JSON with per‑instance metrics).
- Provide starter scripts in the [benchmark code repository](https://github.com/BrunoFu/OR_Agent).
- Describe how to submit results (for example, GitHub pull request or email).

For now, the leaderboard is a template waiting for finalized baseline results.

