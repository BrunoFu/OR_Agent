#!/bin/bash

# Monitor parallel benchmark progress across all 6 batches

cd "$(dirname "${BASH_SOURCE[0]}")"

# Find the most recent batch logs
LATEST_TIMESTAMP=$(ls -t batch_*_*.log 2>/dev/null | head -1 | sed 's/batch_._\(.*\)\.log/\1/')

if [ -z "$LATEST_TIMESTAMP" ]; then
    echo "❌ No batch logs found. Benchmark may not have started yet."
    exit 1
fi

echo "=========================================="
echo "PARALLEL BENCHMARK MONITOR"
echo "=========================================="
echo "Timestamp: $LATEST_TIMESTAMP"
echo "Current time: $(date)"
echo ""

# Function to count completions in a directory
count_completions() {
    local dir="$1"
    if [ -d "$dir" ]; then
        find "$dir" -name "benchmark_results.json" -type f 2>/dev/null | wc -l
    else
        echo "0"
    fi
}

# Function to get batch progress from log
get_batch_progress() {
    local batch_num="$1"
    local log_file="batch_${batch_num}_${LATEST_TIMESTAMP}.log"

    if [ -f "$log_file" ]; then
        # Check if batch is still running
        if ps aux | grep -q "[p]ython.*run_batch_benchmark.*${batch_num}"; then
            status="🔄 RUNNING"
        elif grep -q "Exit code: 0" "$log_file"; then
            status="✅ COMPLETED"
        elif grep -q "Exit code:" "$log_file"; then
            status="❌ FAILED"
        else
            status="🔄 RUNNING"
        fi

        # Get completion count from log
        completed=$(grep -c "Detailed results saved" "$log_file" 2>/dev/null || echo "0")

        echo "$status | $completed instances"
    else
        echo "⏳ NOT STARTED | 0 instances"
    fi
}

# Check each batch
echo "BATCH STATUS:"
echo "----------------------------------------"
echo "Batch 1 (Synthetic L=0, 240):        $(get_batch_progress 1)"
echo "Batch 2 (Synthetic L=4, 240):        $(get_batch_progress 2)"
echo "Batch 3 (Synthetic L=stoch, 240):    $(get_batch_progress 3)"
echo "Batch 4 (Real L=0, 200):             $(get_batch_progress 4)"
echo "Batch 5 (Real L=4, 200):             $(get_batch_progress 5)"
echo "Batch 6 (Real L=stoch, 200):         $(get_batch_progress 6)"
echo ""

# Count total completions from actual result files
echo "VERIFIED COMPLETIONS (from result files):"
echo "----------------------------------------"
syn_0=$(count_completions "examples/benchmark/synthetic_trajectory/lead_time_0")
syn_4=$(count_completions "examples/benchmark/synthetic_trajectory/lead_time_4")
syn_s=$(count_completions "examples/benchmark/synthetic_trajectory/lead_time_stochastic")
real_0=$(count_completions "examples/benchmark/real_trajectory/lead_time_0")
real_4=$(count_completions "examples/benchmark/real_trajectory/lead_time_4")
real_s=$(count_completions "examples/benchmark/real_trajectory/lead_time_stochastic")

echo "Synthetic lead_time_0:        $syn_0 / 240"
echo "Synthetic lead_time_4:        $syn_4 / 240"
echo "Synthetic lead_time_stoch:    $syn_s / 240"
echo "Real lead_time_0:             $real_0 / 200"
echo "Real lead_time_4:             $real_4 / 200"
echo "Real lead_time_stoch:         $real_s / 200"
echo ""

total=$((syn_0 + syn_4 + syn_s + real_0 + real_4 + real_s))
echo "TOTAL: $total / 1320 instances ($(echo "scale=1; $total * 100 / 1320" | bc)%)"
echo ""

# Check running processes
echo "ACTIVE PROCESSES:"
echo "----------------------------------------"
python_procs=$(ps aux | grep -E "[p]ython.*benchmark" | wc -l)
echo "Python benchmark processes: $python_procs"
echo ""

# Show recent errors from logs
echo "RECENT ERRORS (last 5 from all logs):"
echo "----------------------------------------"
grep -h "Error\|Failed\|Exception" batch_*_${LATEST_TIMESTAMP}.log 2>/dev/null | tail -5 | sed 's/^/  /' || echo "  No errors found"
echo ""

echo "To tail a specific batch log:"
echo "  tail -f batch_[1-6]_${LATEST_TIMESTAMP}.log"
echo ""
echo "To view master log:"
echo "  tail -f benchmark_master_parallel_${LATEST_TIMESTAMP}.log"
