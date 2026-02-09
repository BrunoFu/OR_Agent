#!/bin/bash

# Run 10 synthetic lead_time_stochastic instances with improved prompt
# Usage: bash run_improved_benchmark.sh

set -e

# Activate virtual environment
source .venv/bin/activate

# Timestamp for this run
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="benchmark_improved_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo "Starting improved prompt benchmark at $(date)"
echo "Results will be saved to: $OUTPUT_DIR"
echo ""

# Define the 10 test instances (p01-p10, v1, r1_med)
declare -a INSTANCES=(
    "examples/benchmark/synthetic_trajectory/lead_time_stochastic/p01_stationary_iid/v1_normal_100_25/r1_med"
    "examples/benchmark/synthetic_trajectory/lead_time_stochastic/p02_mean_increase/v1_100to200/r1_med"
    "examples/benchmark/synthetic_trajectory/lead_time_stochastic/p03_mean_decrease/v1_100to50/r1_med"
    "examples/benchmark/synthetic_trajectory/lead_time_stochastic/p04_increasing_trend/v1_linear_100t/r1_med"
    "examples/benchmark/synthetic_trajectory/lead_time_stochastic/p05_decreasing_trend/v1_200_minus_3t/r1_med"
    "examples/benchmark/synthetic_trajectory/lead_time_stochastic/p06_variance_change/v1_normal_to_uniform/r1_med"
    "examples/benchmark/synthetic_trajectory/lead_time_stochastic/p07_seasonal/v1_period10_amp30/r1_med"
    "examples/benchmark/synthetic_trajectory/lead_time_stochastic/p08_multi_changepoint/v1_up_then_down/r1_med"
    "examples/benchmark/synthetic_trajectory/lead_time_stochastic/p09_temp_spike_dip/v1_temp_surge/r1_med"
    "examples/benchmark/synthetic_trajectory/lead_time_stochastic/p10_autocorrelated/v1_phi_0_7/r1_med"
)

# Function to run a single instance
run_instance() {
    local INSTANCE_DIR="$1"
    local INSTANCE_NAME=$(basename "$INSTANCE_DIR")
    local PROBLEM_NAME=$(echo "$INSTANCE_DIR" | grep -oP 'p\d+_[^/]+')
    local OUTPUT_FILE="$OUTPUT_DIR/${PROBLEM_NAME}_${INSTANCE_NAME}.log"

    echo "[$PROBLEM_NAME] Starting..."

    python examples/or_to_llm_csv_demo.py \
        --demand-file "${INSTANCE_DIR}/test.csv" \
        --real-instance-train "${INSTANCE_DIR}/train.csv" \
        --promised-lead-time 2 \
        --model "openai/gpt-5-mini" \
        > "$OUTPUT_FILE" 2>&1

    # Extract final reward from output
    REWARD=$(grep -oP "Total Reward.*: \$\K[0-9.-]+" "$OUTPUT_FILE" | tail -1)
    echo "[$PROBLEM_NAME] Completed! Reward: $REWARD"
    echo "$PROBLEM_NAME,$REWARD" >> "$OUTPUT_DIR/results_summary.csv"
}

export -f run_instance
export OUTPUT_DIR

# Initialize results file
echo "Problem,Reward_Improved" > "$OUTPUT_DIR/results_summary.csv"

# Run all instances in parallel (max 5 at a time to avoid rate limits)
echo "Running 10 instances in parallel (5 at a time)..."
echo ""

printf '%s\n' "${INSTANCES[@]}" | xargs -n 1 -P 5 -I {} bash -c 'run_instance "{}"'

echo ""
echo "=========================================="
echo "All runs completed at $(date)"
echo "=========================================="
echo ""

# Generate comparison report
python3 << 'PYTHON_SCRIPT'
import json
import csv
import os
from pathlib import Path

output_dir = os.environ['OUTPUT_DIR']
results_file = f"{output_dir}/results_summary.csv"

# Read improved results
improved_results = {}
with open(results_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        improved_results[row['Problem']] = float(row['Reward_Improved'])

# Read original results
original_results = {}
base_dir = "examples/benchmark/synthetic_trajectory/lead_time_stochastic"
problems = {
    "p01_stationary_iid": "v1_normal_100_25",
    "p02_mean_increase": "v1_100to200",
    "p03_mean_decrease": "v1_100to50",
    "p04_increasing_trend": "v1_linear_100t",
    "p05_decreasing_trend": "v1_200_minus_3t",
    "p06_variance_change": "v1_normal_to_uniform",
    "p07_seasonal": "v1_period10_amp30",
    "p08_multi_changepoint": "v1_up_then_down",
    "p09_temp_spike_dip": "v1_temp_surge",
    "p10_autocorrelated": "v1_phi_0_7"
}

for prob, variant in problems.items():
    result_file = f"{base_dir}/{prob}/{variant}/r1_med/benchmark_results.json"
    if os.path.exists(result_file):
        with open(result_file, 'r') as f:
            data = json.load(f)
            original_results[prob] = data['results']['or_to_llm']['mean']

# Generate comparison report
print("\n" + "="*80)
print("COMPARISON: Original vs Improved Prompt")
print("="*80)
print(f"{'Problem':<30} {'Original':<12} {'Improved':<12} {'Change':<12} {'% Change':<12}")
print("-"*80)

total_original = 0
total_improved = 0
improvements = []

for prob in sorted(original_results.keys()):
    orig = original_results[prob]
    impr = improved_results.get(prob, 0)
    change = impr - orig
    pct_change = (change / orig * 100) if orig != 0 else 0

    total_original += orig
    total_improved += impr
    improvements.append(pct_change)

    symbol = "✓" if change > 0 else "✗" if change < 0 else "="
    print(f"{prob:<30} {orig:<12.1f} {impr:<12.1f} {change:+11.1f} {pct_change:+11.1f}% {symbol}")

print("-"*80)
total_change = total_improved - total_original
total_pct = (total_change / total_original * 100) if total_original != 0 else 0
avg_improvement = sum(improvements) / len(improvements)

print(f"{'TOTAL':<30} {total_original:<12.1f} {total_improved:<12.1f} {total_change:+11.1f} {total_pct:+11.1f}%")
print(f"{'AVERAGE IMPROVEMENT':<30} {'':<12} {'':<12} {'':<12} {avg_improvement:+11.1f}%")
print("="*80)

# Save detailed comparison
comparison_file = f"{output_dir}/comparison_report.txt"
with open(comparison_file, 'w') as f:
    f.write("Comparison Report: Original vs Improved Prompt\n")
    f.write("="*80 + "\n\n")
    for prob in sorted(original_results.keys()):
        orig = original_results[prob]
        impr = improved_results.get(prob, 0)
        change = impr - orig
        pct_change = (change / orig * 100) if orig != 0 else 0
        f.write(f"{prob}: {orig:.1f} → {impr:.1f} ({change:+.1f}, {pct_change:+.1f}%)\n")
    f.write(f"\nTotal improvement: {total_pct:+.1f}%\n")
    f.write(f"Average improvement: {avg_improvement:+.1f}%\n")

print(f"\nDetailed report saved to: {comparison_file}")
print(f"Full logs available in: {output_dir}/")

PYTHON_SCRIPT

echo ""
echo "Benchmark complete!"
