# Benchmark Leaderboard Builder

This directory contains code for building leaderboard statistics from benchmark results.

## Overview

The `build_stats.py` script aggregates performance metrics from benchmark result files and generates leaderboard data files for the benchmark website.

## Usage

```bash
python examples/benchmark_leaderboard/build_stats.py
```

## What It Does

1. **Scans benchmark directories**: Finds all `*_bench` directories in `examples/`
2. **Aggregates results**: Reads `benchmark_results.json` files from each benchmark directory
3. **Calculates statistics**: Computes average normalized reward per LLM+Method combination
4. **Generates output files**:
   - `_data/leaderboard.yml` - YAML format for Jekyll sites
   - `data/leaderboard.json` - JSON format for static HTML sites

## Output Structure

The generated JSON/YAML contains a `methods` array, where each entry represents a unique LLM+Method combination with:

- `llm_id`: Identifier for the LLM (e.g., "gemini-3-flash")
- `llm_label`: Human-readable LLM name (e.g., "Gemini 3 Flash")
- `method_id`: Method identifier (e.g., "or_to_llm")
- `method_label`: Human-readable method name (e.g., "OR→LLM")
- `mean_ratio`: Average normalized reward across all instances
- `by_family_mean_ratio`: Average by dataset family (synthetic_trajectory, real_trajectory)
- `by_lead_mean_ratio`: Average by lead-time setting (lead_time_0, lead_time_4, lead_time_stochastic)

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)

## Reusability

This code is designed to be reusable for other benchmark projects. To adapt it:

1. Update `LLM_LABELS` and `METHOD_LABELS` dictionaries with your labels
2. Adjust `BENCH_DIR_SUFFIX` if your benchmark directories use a different naming pattern
3. Modify output paths if needed (currently writes to repo root)
