# GPT-5-Mini Improved Prompt - Benchmark Suite

## Overview

This branch contains improved prompts for GPT-5-mini to address two critical issues identified in lead_time_stochastic benchmarks:

### Issue 1: Over-ordering in Early Periods
**Problem**: GPT-5-mini didn't trust OR's (L+1)-period coverage calculations, recalculating from scratch and over-ordering by ~100%

**Fix**: Added explicit clarification that OR already accounts for (L+1)-period coverage via μ̂ = (1+L) × μ̄

### Issue 2: Under-ordering in Late Periods (Lost Inventory Tracking)
**Problem**: GPT-5-mini trusted the "In-transit" value blindly, not realizing it includes lost orders that will never arrive, leading to many periods of ordering 0

**Fix**: Added instructions to actively track lost shipments and calculate real_pipeline = in-transit - sum(lost_orders)

## Expected Improvements

Based on initial testing (10 instances):

| Metric | Original GPT-5-mini | Expected Improved | Grok-4.1-fast (Target) |
|--------|---------------------|-------------------|------------------------|
| or_to_llm reward | ~3,000-4,000 | ~9,000-11,000 | ~10,000-11,000 |
| % of perfect | ~13-17% | ~38-45% | ~43-45% |
| Improvement | - | **+150-200%** | - |

## Files Modified

- `examples/or_to_llm_csv_demo.py` - Added two critical prompt sections (lines 804-819)
- `run_improved_benchmark.sh` - Test script for 10 instances
- `run_full_benchmark_tmux.sh` - Full benchmark script for all 1,320 instances
- `compare_with_original.sh` - Comparison analysis script

## Backup

Original benchmark results (1,320 instances) backed up to:
- `examples/benchmark_ORIGINAL_20260209/` (511MB, added to .gitignore)

## Running the Full Benchmark

### 1. Test Run (10 instances)
```bash
bash run_improved_benchmark.sh
```

### 2. Full Run (1,320 instances)
```bash
bash run_full_benchmark_tmux.sh
```

This will:
- Create a tmux session named `gpt5mini_improved_full`
- Run 10 workers in parallel
- Save logs to `benchmark_logs_improved_YYYYMMDD_HHMMSS/`
- Estimated time: ~20-30 hours for all 1,320 instances

### 3. Monitor Progress

Inside tmux:
```bash
tmux attach -t gpt5mini_improved_full
```

Detach: `Ctrl+B`, then `D`

Check progress from outside tmux:
```bash
tail -f benchmark_logs_improved_*/progress.log
```

### 4. Generate Comparison Report
```bash
bash compare_with_original.sh benchmark_logs_improved_YYYYMMDD_HHMMSS/
```

## Prompt Changes Details

### Section 1: OR Coverage Trust (Line 804-809)
```
⚠️ CRITICAL: OR's recommendation ALREADY accounts for (L+1)-period coverage via μ̂ = (1+L) × μ̄!
The base_stock formula includes both expected demand over (L+1) periods AND safety stock (z*σ̂).
DO NOT recalculate (L+1)-period coverage from scratch - OR has already done this!
Only override OR if you have STRONG EVIDENCE (confirmed lead time changes, sustained demand
regime shifts, lost shipments, or calendar-driven events).
```

### Section 2: Lost Shipment Tracking (Line 811-819)
```
⚠️ CRITICAL: LOST SHIPMENT TRACKING
The 'In-transit' value shows ALL undelivered orders, including LOST shipments that will NEVER arrive!
You MUST actively track which orders are lost:
- If an order hasn't concluded after (promised_lead_time + 3) periods, it's likely LOST
- Maintain a 'real pipeline' by subtracting confirmed/suspected lost orders from In-transit
- DO NOT trust In-transit at face value - it inflates over time as lost orders accumulate!
- Example: If In-transit=520 but orders from P5, P12, P18 (total 300 units) are overdue 5+ periods,
  then real_pipeline = 520 - 300 = 220. Use this REAL pipeline for coverage calculations.
- When you calculate whether 'pipeline covers X periods', use (on-hand + real_pipeline), NOT raw in-transit!
```

## Example Improvements

### Period 1 Behavior
- **Before**: OR recommends 71 → GPT orders 149 (+110% over-order)
- **After**: OR recommends 71 → GPT orders 71 (follows OR appropriately)

### Period 30 Behavior
- **Before**: In-transit=520 → "covers demand" → order 0 (ignoring 300+ lost units)
- **After**: "real_pipeline = 520 - 300 = 220" → order 80 to fill shortfall

## Credits

Analysis and improvements developed through collaboration identifying:
1. GPT-5-mini's misunderstanding of OR's coverage calculations
2. GPT-5-mini's failure to track lost inventory (discovered by observing many 0 orders in late periods)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
