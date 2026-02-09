---
layout: page
title: Leaderboard
permalink: /leaderboard
---

# Leaderboard

This page summarizes performance of OR baselines, LLM policies, and OR–LLM hybrids on the **AI Agents for Inventory Control Benchmark**.

The primary evaluation metric is **cumulative reward** over the test period. We also report **normalized reward**, defined as the ratio between actual reward and a perfect‑foresight upper bound.

## Overall leaderboard

The table below ranks all evaluated combinations of LLM and decision method by **average normalized reward** across all 1,320 benchmark instances. Higher is better, and 1.0 corresponds to the perfect‑foresight upper bound.

| Rank | LLM | Method | Avg Normalized Reward | Details |
|------|-----|--------|-----------------------|---------|
{% assign rows = site.data.leaderboard.methods %}
{% assign sorted = rows | sort: "mean_ratio" | reverse %}
{% for row in sorted %}
| {{ forloop.index }} | {{ row.llm_label }} | {{ row.method_label }} | {{ row.mean_ratio | round: 3 }} | [View]({{ '/leaderboard/' | append: row.llm_id | append: '/' | append: row.method_id | relative_url }}) |
{% endfor %}

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

## Method-level breakdown (per LLM × method)

For each row in the leaderboard, the detail page shows:

- The underlying model name (for example, `google/gemini-3-flash-preview`).
- Average normalized reward by dataset family:
  - `synthetic_trajectory` (720 instances)
  - `real_trajectory` (600 instances)
- Average normalized reward by lead‑time setting:
  - `lead_time_0`, `lead_time_4`, `lead_time_stochastic`

In future iterations we can further extend these pages with per‑instance tables and links into raw `benchmark_results.json` files.

