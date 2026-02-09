#!/bin/bash

# Run complete benchmark suite (1,320 instances) with improved prompt
# Using the existing run_batch_benchmark.py infrastructure
# Usage: bash run_all_benchmarks_improved.sh

set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

# Configuration
PARALLEL_INSTANCES=20
MODEL="openai/gpt-5-mini"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MASTER_LOG="benchmark_master_improved_${TIMESTAMP}.log"

echo "=========================================="  | tee -a "$MASTER_LOG"
echo "GPT-5-MINI IMPROVED PROMPT - FULL BENCHMARK" | tee -a "$MASTER_LOG"
echo "==========================================" | tee -a "$MASTER_LOG"
echo "Started: $(date)" | tee -a "$MASTER_LOG"
echo "Model: $MODEL" | tee -a "$MASTER_LOG"
echo "Parallel instances: $PARALLEL_INSTANCES" | tee -a "$MASTER_LOG"
echo "Master log: $MASTER_LOG" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# Check if original results are backed up
if [ ! -d "examples/benchmark_ORIGINAL_20260209" ]; then
    echo "❌ ERROR: Original results not backed up!" | tee -a "$MASTER_LOG"
    echo "Run this first to backup:" | tee -a "$MASTER_LOG"
    echo "  cp -r examples/benchmark/real_trajectory examples/benchmark_ORIGINAL_20260209/real_trajectory" | tee -a "$MASTER_LOG"
    echo "  cp -r examples/benchmark/synthetic_trajectory examples/benchmark_ORIGINAL_20260209/synthetic_trajectory" | tee -a "$MASTER_LOG"
    exit 1
fi

echo "✓ Original results backed up" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# Function to run a batch and log results
run_batch() {
    local batch_name="$1"
    local base_dir="$2"
    local instances_count="$3"

    echo "=========================================="
    echo "BATCH: $batch_name ($instances_count instances)"
    echo "=========================================="
    echo "Base directory: $base_dir"
    echo "Started: $(date)"
    echo ""

    # Run the batch benchmark (with --force to overwrite existing results)
    uv run python examples/run_batch_benchmark.py \
        --base-dir "$base_dir" \
        --parallel-instances "$PARALLEL_INSTANCES" \
        --force \
        --model "$MODEL"

    exit_code=$?

    echo ""
    echo "Completed: $(date)"
    echo "Exit code: $exit_code"
    echo ""

    return $exit_code
}

# Run all batches
echo "Starting benchmark batches..." | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# Batch 1: Synthetic L=0 (240 instances)
echo "======================================" | tee -a "$MASTER_LOG"
echo "Batch 1/6: Synthetic lead_time_0" | tee -a "$MASTER_LOG"
echo "======================================" | tee -a "$MASTER_LOG"
run_batch "Synthetic L=0" "examples/benchmark/synthetic_trajectory/lead_time_0" "240" 2>&1 | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# Batch 2: Synthetic L=4 (240 instances)
echo "======================================" | tee -a "$MASTER_LOG"
echo "Batch 2/6: Synthetic lead_time_4" | tee -a "$MASTER_LOG"
echo "======================================" | tee -a "$MASTER_LOG"
run_batch "Synthetic L=4" "examples/benchmark/synthetic_trajectory/lead_time_4" "240" 2>&1 | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# Batch 3: Synthetic L=stochastic (240 instances) - THE CRITICAL ONE!
echo "======================================" | tee -a "$MASTER_LOG"
echo "Batch 3/6: Synthetic lead_time_stochastic ⭐" | tee -a "$MASTER_LOG"
echo "======================================" | tee -a "$MASTER_LOG"
run_batch "Synthetic L=stochastic" "examples/benchmark/synthetic_trajectory/lead_time_stochastic" "240" 2>&1 | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# Batch 4: Real L=0 (200 instances)
echo "======================================" | tee -a "$MASTER_LOG"
echo "Batch 4/6: Real lead_time_0" | tee -a "$MASTER_LOG"
echo "======================================" | tee -a "$MASTER_LOG"
run_batch "Real L=0" "examples/benchmark/real_trajectory/lead_time_0" "200" 2>&1 | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# Batch 5: Real L=4 (200 instances)
echo "======================================" | tee -a "$MASTER_LOG"
echo "Batch 5/6: Real lead_time_4" | tee -a "$MASTER_LOG"
echo "======================================" | tee -a "$MASTER_LOG"
run_batch "Real L=4" "examples/benchmark/real_trajectory/lead_time_4" "200" 2>&1 | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# Batch 6: Real L=stochastic (200 instances) - ALSO CRITICAL!
echo "======================================" | tee -a "$MASTER_LOG"
echo "Batch 6/6: Real lead_time_stochastic ⭐" | tee -a "$MASTER_LOG"
echo "======================================" | tee -a "$MASTER_LOG"
run_batch "Real L=stochastic" "examples/benchmark/real_trajectory/lead_time_stochastic" "200" 2>&1 | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# Final summary
echo "=========================================="  | tee -a "$MASTER_LOG"
echo "ALL BATCHES COMPLETED" | tee -a "$MASTER_LOG"
echo "=========================================="  | tee -a "$MASTER_LOG"
echo "Finished: $(date)" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"
echo "Master log: $MASTER_LOG" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"
echo "To generate comparison report:" | tee -a "$MASTER_LOG"
echo "  python examples/compare_benchmarks.py" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"
