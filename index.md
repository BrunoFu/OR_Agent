---
layout: page
title: Home
permalink: /
---

# AI Agents for Inventory Control Benchmark

A 1,320‑instance benchmark for stress‑testing OR and LLM‑based agents under non‑stationary demand and uncertain lead times.

<div class="hero-actions">
  <a class="hero-button primary" href="https://huggingface.co/datasets/Yaopeng12138/inventory_control_benchmark_instances" target="_blank" rel="noopener">Dataset</a>
  <a class="hero-button" href="https://github.com/BrunoFu/OR_Agent" target="_blank" rel="noopener">Code</a>
  <a class="hero-button" href="{{ '/leaderboard' | relative_url }}">Leaderboard</a>
  <span class="hero-button">Paper (coming soon)</span>
</div>

Benchmark for OR‑ and LLM‑based inventory agents on synthetic and real trajectories.

<div class="two-column">
  <div>
    <div class="card">
      <h2>Why this benchmark?</h2>
      <p>
        Classical inventory algorithms from operations research perform well when demand and lead times are stable and correctly modeled.
        In many real systems, however, demand shifts over time, seasonality appears, and supply is unreliable, so standard predict‑then‑optimize pipelines can break.
      </p>
      <p>
        Recent large language models can reason with rich contextual descriptions and adapt to regime changes, but they are not a drop‑in replacement for well‑understood OR heuristics.
        Practitioners need a controlled way to study when LLM agents help, when they hurt, and how they should be combined with traditional tools.
      </p>
      <p>
        This benchmark provides a common testbed for multi‑period inventory control with challenging demand and lead‑time patterns, enabling apples‑to‑apples comparisons between OR baselines, LLM agents, and hybrid methods.
      </p>
    </div>

    <div class="card">
      <h2>Benchmark design</h2>
      <p>
        Each benchmark instance is a finite‑horizon inventory game defined by a fixed demand and arrival trajectory, with profit from sales and holding costs on leftover stock.
      </p>
      <ul>
        <li><strong>Synthetic trajectories (720 instances)</strong>: 10 demand patterns × 4 variants, with shocks, trends, variance changes, seasonality, temporary spikes/dips, and autocorrelated AR(1) behavior.</li>
        <li><strong>Real trajectories (600 instances)</strong>: weekly sales for 200 retail products, each combined with three lead‑time settings and cost structures.</li>
        <li><strong>Lead times and lost orders</strong>: immediate delivery, fixed‑delay delivery, and stochastic lead times where orders may be delayed or never arrive.</li>
      </ul>
    </div>
  </div>

  <aside>
    <div class="card">
      <h2>Leaderboard (preview)</h2>
      <p>
        We evaluate OR baselines, LLM policies, and OR–LLM hybrids on the full set of 1,320 instances.
        The table below will show the current top methods; a full leaderboard is available on the dedicated page.
      </p>
      <table class="leaderboard-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Method</th>
            <th>LLM</th>
            <th>Setting</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>–</td>
            <td>Coming soon</td>
            <td>–</td>
            <td>–</td>
            <td>–</td>
          </tr>
        </tbody>
      </table>
      <div class="leaderboard-footer">
        <a href="{{ '/leaderboard' | relative_url }}">View full leaderboard</a>
      </div>
    </div>
  </aside>
</div>

## Benchmark at a glance

<div class="glance-grid">
  <div class="card">
    <div class="glance-card-title">1,320 instances</div>
    <p>Synthetic and real inventory trajectories for controlled experiments.</p>
  </div>
  <div class="card">
    <div class="glance-card-title">2 benchmark families</div>
    <p>Synthetic stress tests and real‑data demand from retail products.</p>
  </div>
  <div class="card">
    <div class="glance-card-title">Lead‑time regimes</div>
    <p>Immediate, fixed, and stochastic lead times, including lost orders.</p>
  </div>
  <div class="card">
    <div class="glance-card-title">Methods and agents</div>
    <p>OR baselines, LLM agents, and OR–LLM hybrids (results coming soon).</p>
  </div>
</div>

## Dataset overview

The benchmark is organized as a collection of instance directories. Each directory contains two CSV files:

- <code>train.csv</code>: five historical demand observations per instance.
- <code>test.csv</code>: the demand trajectory and associated lead times and cost parameters used for evaluation.

See the dataset page for full details on directory layout and file formats.

[Explore the dataset]({{ '/dataset' | relative_url }})

