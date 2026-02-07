# OR-to-LLM Standalone Testing Guide

## Overview

This document explains how the OR-to-LLM algorithm works in the web interface (instances 1-3) and how to test it standalone to measure its baseline performance without human decisions.

## How Web Interface Works

### Architecture

The web interface (`examples/fullstack_demo/`) provides three modes:

- **Mode A (OR Only)**: Pure OR base-stock policy, no LLM
- **Mode B (OR → LLM with Human Feedback)**: OR provides recommendations, LLM sees them and makes initial decisions, then human can provide feedback
- **Mode C (OR → LLM with Periodic Guidance)**: OR provides recommendations, LLM makes autonomous decisions for multiple periods, human provides periodic strategic guidance

### Instances

The web interface uses three H&M retail instances:

1. **Instance 1 (599580017)**: Swimwear product, promised lead time = 0 periods
2. **Instance 2 (568601006)**: Retail product, promised lead time = 1 period
3. **Instance 3 (706016001)**: Retail product, promised lead time = 1 period

### Mode B and Mode C Algorithm

Both Mode B and Mode C use the **OR-to-LLM** algorithm:

```python
# Located in: examples/or_to_llm_csv_demo.py
# Called by: examples/fullstack_demo/backend/simulation_current.py

def make_hybrid_vm_agent(
    initial_samples: dict,
    promised_lead_time: int,
    human_feedback_enabled: bool = False,  # True for Mode B
    guidance_enabled: bool = False         # True for Mode C
):
    """
    Creates an LLM agent that:
    1. Receives OR recommendations (base-stock policy with cap)
    2. Sees current inventory state and demand history
    3. Makes ordering decisions considering OR baseline
    4. Can adjust OR recommendations based on:
       - Actual vs. promised lead time
       - Demand regime changes
       - Seasonality from exact dates
       - Lost shipments or pipeline anomalies
    """
```

#### OR Algorithm (Base-Stock with Cap)

The OR component calculates recommendations using:

- **Demand estimation**: μ̂ = (1+L) × empirical_mean, σ̂ = √(1+L) × empirical_std
- **Base stock**: base_stock = μ̂ + z*σ̂, where z* = Φ⁻¹(profit/(profit+holding_cost))
- **Capped order**: order = max(0, min(base_stock - pipeline, cap))
  - Cap prevents large swings: cap = μ̂/(1+L) + Φ⁻¹(0.95) × σ̂/√(1+L)

#### LLM Decision Making

The LLM agent:
1. Reads OR recommendation with full statistics
2. Analyzes recent demand patterns vs. historical
3. Infers actual lead time from concluded periods
4. Considers seasonality using exact dates and SKU description
5. Decides whether to follow, scale, or override OR recommendation
6. Provides rationale explaining adjustment path

### Human Interaction

- **Mode B**: Human can provide feedback after seeing LLM's initial proposal, then LLM adjusts
- **Mode C**: Human provides strategic guidance every N periods (e.g., "expect 30% demand increase next month"), LLM incorporates it into all decisions

## Testing OR-to-LLM Standalone

### Objective

Measure the **baseline performance** of the OR-to-LLM algorithm without human decisions or guidance. This tells us:

1. How well the algorithm performs autonomously
2. The value added by human decisions (comparing Mode B/C results with vs. without human input)
3. Whether the LLM effectively uses OR recommendations

### Test Script

Use the provided test script:

```bash
python test_or_to_llm_standalone.py
```

This script:
1. Loads each instance (1, 2, 3) configuration
2. Runs `or_to_llm_csv_demo.py` without human feedback or guidance flags
3. Collects final performance metrics (total reward)
4. Compares across instances

### Manual Testing

You can also test a single instance manually:

```bash
cd examples

# Instance 1 (Swimwear, lead time = 0)
python or_to_llm_csv_demo.py \
  --demand-file H&M_instances/599580017/test.csv \
  --real-instance-train H&M_instances/599580017/train.csv \
  --promised-lead-time 0

# Instance 2 (lead time = 1)
python or_to_llm_csv_demo.py \
  --demand-file H&M_instances/568601006/test.csv \
  --real-instance-train H&M_instances/568601006/train.csv \
  --promised-lead-time 1

# Instance 3 (lead time = 1)
python or_to_llm_csv_demo.py \
  --demand-file H&M_instances/706016001/test.csv \
  --real-instance-train H&M_instances/706016001/train.csv \
  --promised-lead-time 1
```

### Understanding Results

The script will output:

1. **Period-by-period decisions**: Shows OR recommendation vs. LLM final decision
2. **Total reward**: Sum of (profit × units_sold - holding_cost × ending_inventory)
3. **Decision rationale**: LLM's explanation for each adjustment

Look for:
- How often LLM follows vs. overrides OR recommendations
- Types of adjustments made (increase for seasonality, decrease for regime change, etc.)
- Performance compared to pure OR baseline (Mode A)

## Comparison Framework

| Mode | Algorithm | Human Input | Testing Goal |
|------|-----------|-------------|--------------|
| Mode A | OR only | None | Baseline OR performance |
| Mode B (no human) | OR → LLM | None (autonomous) | **This test**: OR-to-LLM baseline |
| Mode B (with human) | OR → LLM → Human | Feedback each period | Human-in-loop value |
| Mode C (no guidance) | OR → LLM | None (autonomous) | **This test**: OR-to-LLM baseline |
| Mode C (with guidance) | OR → LLM | Strategic guidance every N periods | Guidance value |

## Web Interface Flow

### Backend Code Path

1. **Start game**: `app.py:start_run()` creates `SimulationSession`
2. **Session init**: `simulation_current.py:__init__()` initializes:
   - CSV demand player
   - OR agent (if enabled)
   - LLM agent via `make_hybrid_vm_agent()`
3. **Each period**:
   - OR agent: `get_recommendation()` → calculates order with stats
   - LLM agent: `__call__()` → sees OR recommendation + observation → makes decision
   - (Mode B) Human sees LLM proposal → can provide feedback → LLM adjusts
   - (Mode C) LLM plays N periods → human provides guidance → LLM continues

### Frontend Code Path

- **Mode B**: `frontend/modeB.html`
  - Shows OR recommendation panel
  - Shows LLM proposal with rationale
  - Provides feedback input box
  - Submits final action

- **Mode C**: `frontend/modeC.html`
  - Auto-plays multiple periods
  - Pauses every N periods for guidance
  - Shows guidance input
  - Continues auto-play

## Key Files

- `examples/or_to_llm_csv_demo.py`: Main OR-to-LLM algorithm
- `examples/or_csv_demo.py`: OR base-stock policy implementation
- `examples/fullstack_demo/backend/simulation_current.py`: Web interface simulation
- `examples/fullstack_demo/backend/app.py`: FastAPI endpoints
- `test_or_to_llm_standalone.py`: This standalone test script

## Expected Performance Patterns

Based on the algorithm design:

1. **Early periods**: LLM should closely follow OR (limited history)
2. **Seasonality**: LLM may increase orders before demand spikes (using dates)
3. **Regime shifts**: LLM should detect and adjust faster than OR (which uses all history equally)
4. **Lead time**: LLM should adapt if actual lead time differs from promised
5. **Overall**: OR-to-LLM should outperform pure OR, but by how much?

Compare your results to:
- Pure OR (Mode A) results from leaderboard
- Human-guided results (Mode B/C with decisions) from leaderboard

## Troubleshooting

**Error: OpenAI API key not found**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**Error: CSV not found**
- Check that you're running from the repository root
- Verify H&M_instances folder exists with subfolder structure

**Error: Import failed**
- Ensure `textarena` package is installed: `pip install -e .`
- Check Python path includes examples directory

**Performance seems too low/high**
- Verify you're using the correct promised lead time for each instance
- Check that train.csv is being loaded (provides initial samples)
- Review LLM decisions in output to see if adjustments make sense

## Next Steps

After running this test:

1. **Compare to Mode A**: How much does LLM improve over pure OR?
2. **Analyze decisions**: When does LLM override OR? Are adjustments justified?
3. **Estimate human value**: Compare to Mode B/C results with human input
4. **Iterate on prompt**: Can you improve LLM decision quality by refining the system prompt?
