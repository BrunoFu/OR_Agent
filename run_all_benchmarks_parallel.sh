#!/bin/bash

# Run complete benchmark suite (1,320 instances) with ALL BATCHES IN PARALLEL
# AGGRESSIVE MODE: All 6 batches run simultaneously
# Usage: bash run_all_benchmarks_parallel.sh

set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

# Configuration
PARALLEL_INSTANCES=20
MODEL="openai/gpt-5-mini"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MASTER_LOG="benchmark_master_parallel_${TIMESTAMP}.log"

echo "=========================================="  | tee -a "$MASTER_LOG"
echo "GPT-5-MINI - PARALLEL BATCH MODE" | tee -a "$MASTER_LOG"
echo "ALL 6 BATCHES RUNNING SIMULTANEOUSLY" | tee -a "$MASTER_LOG"
echo "==========================================" | tee -a "$MASTER_LOG"
echo "Started: $(date)" | tee -a "$MASTER_LOG"
echo "Model: $MODEL" | tee -a "$MASTER_LOG"
echo "Parallel instances per batch: $PARALLEL_INSTANCES" | tee -a "$MASTER_LOG"
echo "Total batches: 6 (all in parallel)" | tee -a "$MASTER_LOG"
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

# Function to run a batch in background
run_batch() {
    local batch_num="$1"
    local batch_name="$2"
    local base_dir="$3"
    local instances_count="$4"
    local batch_log="batch_${batch_num}_${TIMESTAMP}.log"

    {
        echo "=========================================="
        echo "BATCH $batch_num: $batch_name ($instances_count instances)"
        echo "=========================================="
        echo "Base directory: $base_dir"
        echo "Started: $(date)"
        echo ""

        # Run the batch benchmark (with --skip-completed to skip done instances)
        uv run python examples/run_batch_benchmark.py \
            --base-dir "$base_dir" \
            --parallel-instances "$PARALLEL_INSTANCES" \
            --skip-completed \
            --model "$MODEL"

        exit_code=$?

        echo ""
        echo "Completed: $(date)"
        echo "Exit code: $exit_code"
        echo ""
    } > "$batch_log" 2>&1

    return $exit_code
}

# Launch all batches in parallel
echo "Launching all 6 batches in parallel..." | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# Store PIDs for tracking
declare -a batch_pids

# Batch 1: Synthetic L=0 (240 instances)
echo "Starting Batch 1/6: Synthetic lead_time_0" | tee -a "$MASTER_LOG"
run_batch "1" "Synthetic L=0" "examples/benchmark/synthetic_trajectory/lead_time_0" "240" &
batch_pids[1]=$!

# Batch 2: Synthetic L=4 (240 instances)
echo "Starting Batch 2/6: Synthetic lead_time_4" | tee -a "$MASTER_LOG"
run_batch "2" "Synthetic L=4" "examples/benchmark/synthetic_trajectory/lead_time_4" "240" &
batch_pids[2]=$!

# Batch 3: Synthetic L=stochastic (240 instances) - THE CRITICAL ONE!
echo "Starting Batch 3/6: Synthetic lead_time_stochastic ⭐" | tee -a "$MASTER_LOG"
run_batch "3" "Synthetic L=stochastic" "examples/benchmark/synthetic_trajectory/lead_time_stochastic" "240" &
batch_pids[3]=$!

# Batch 4: Real L=0 (200 instances)
echo "Starting Batch 4/6: Real lead_time_0" | tee -a "$MASTER_LOG"
run_batch "4" "Real L=0" "examples/benchmark/real_trajectory/lead_time_0" "200" &
batch_pids[4]=$!

# Batch 5: Real L=4 (200 instances)
echo "Starting Batch 5/6: Real lead_time_4" | tee -a "$MASTER_LOG"
run_batch "5" "Real L=4" "examples/benchmark/real_trajectory/lead_time_4" "200" &
batch_pids[5]=$!

# Batch 6: Real L=stochastic (200 instances) - ALSO CRITICAL!
echo "Starting Batch 6/6: Real lead_time_stochastic ⭐" | tee -a "$MASTER_LOG"
run_batch "6" "Real L=stochastic" "examples/benchmark/real_trajectory/lead_time_stochastic" "200" &
batch_pids[6]=$!

echo "" | tee -a "$MASTER_LOG"
echo "All 6 batches launched!" | tee -a "$MASTER_LOG"
echo "Batch 1 PID: ${batch_pids[1]}" | tee -a "$MASTER_LOG"
echo "Batch 2 PID: ${batch_pids[2]}" | tee -a "$MASTER_LOG"
echo "Batch 3 PID: ${batch_pids[3]}" | tee -a "$MASTER_LOG"
echo "Batch 4 PID: ${batch_pids[4]}" | tee -a "$MASTER_LOG"
echo "Batch 5 PID: ${batch_pids[5]}" | tee -a "$MASTER_LOG"
echo "Batch 6 PID: ${batch_pids[6]}" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"
echo "Waiting for all batches to complete..." | tee -a "$MASTER_LOG"
echo "Individual batch logs:" | tee -a "$MASTER_LOG"
echo "  - batch_1_${TIMESTAMP}.log" | tee -a "$MASTER_LOG"
echo "  - batch_2_${TIMESTAMP}.log" | tee -a "$MASTER_LOG"
echo "  - batch_3_${TIMESTAMP}.log" | tee -a "$MASTER_LOG"
echo "  - batch_4_${TIMESTAMP}.log" | tee -a "$MASTER_LOG"
echo "  - batch_5_${TIMESTAMP}.log" | tee -a "$MASTER_LOG"
echo "  - batch_6_${TIMESTAMP}.log" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# Wait for all batches to complete
wait

# Check exit codes
echo "=========================================="  | tee -a "$MASTER_LOG"
echo "ALL BATCHES COMPLETED" | tee -a "$MASTER_LOG"
echo "=========================================="  | tee -a "$MASTER_LOG"
echo "Finished: $(date)" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# Check for errors in individual logs
echo "Checking batch results..." | tee -a "$MASTER_LOG"
for i in {1..6}; do
    batch_log="batch_${i}_${TIMESTAMP}.log"
    if [ -f "$batch_log" ]; then
        exit_code=$(grep "Exit code:" "$batch_log" | tail -1 | awk '{print $3}')
        if [ "$exit_code" == "0" ]; then
            echo "✓ Batch $i: SUCCESS" | tee -a "$MASTER_LOG"
        else
            echo "✗ Batch $i: FAILED (exit code: $exit_code)" | tee -a "$MASTER_LOG"
        fi
    else
        echo "⚠ Batch $i: Log file not found" | tee -a "$MASTER_LOG"
    fi
done
echo "" | tee -a "$MASTER_LOG"

echo "Master log: $MASTER_LOG" | tee -a "$MASTER_LOG"
echo "Individual batch logs: batch_[1-6]_${TIMESTAMP}.log" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"
echo "To generate comparison report:" | tee -a "$MASTER_LOG"
echo "  python examples/compare_benchmarks.py" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"
