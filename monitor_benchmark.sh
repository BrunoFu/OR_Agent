#!/bin/bash

# Monitor benchmark progress across all 6 batches
# Usage: bash monitor_benchmark.sh
# Or: watch -n 30 bash monitor_benchmark.sh

clear

echo "================================================================================"
echo "BENCHMARK PROGRESS MONITOR - $(date '+%H:%M:%S')"
echo "================================================================================"
echo ""

# Define batches
declare -a BATCHES=(
    "Batch 1/6|examples/benchmark/synthetic_trajectory/lead_time_0|240"
    "Batch 2/6|examples/benchmark/synthetic_trajectory/lead_time_4|240"
    "Batch 3/6|examples/benchmark/synthetic_trajectory/lead_time_stochastic|240"
    "Batch 4/6|examples/benchmark/real_trajectory/lead_time_0|200"
    "Batch 5/6|examples/benchmark/real_trajectory/lead_time_4|200"
    "Batch 6/6|examples/benchmark/real_trajectory/lead_time_stochastic|200"
)

# Find batch start time
BATCH_LOG="examples/benchmark/synthetic_trajectory/lead_time_0/batch_log_20260209_011515.txt"
if [ -f "$BATCH_LOG" ]; then
    START_TIME=$(stat -c %Y "$BATCH_LOG" 2>/dev/null || stat -f %m "$BATCH_LOG" 2>/dev/null)
    CURRENT_TIME=$(date +%s)
    ELAPSED_MIN=$(( (CURRENT_TIME - START_TIME) / 60 ))
else
    ELAPSED_MIN=0
fi

TOTAL_INSTANCES=0
TOTAL_COMPLETED=0
TOTAL_NEW=0

for batch_info in "${BATCHES[@]}"; do
    IFS='|' read -r batch_name base_dir expected_count <<< "$batch_info"

    # Count all completed instances
    completed=$(find "$base_dir" -name "benchmark_results.json" 2>/dev/null | wc -l)

    # Count newly completed (updated after batch start)
    if [ -f "$BATCH_LOG" ]; then
        new_completed=$(find "$base_dir" -name "benchmark_results.json" -newer "$BATCH_LOG" 2>/dev/null | wc -l)
    else
        new_completed=0
    fi

    TOTAL_INSTANCES=$((TOTAL_INSTANCES + expected_count))
    TOTAL_COMPLETED=$((TOTAL_COMPLETED + completed))
    TOTAL_NEW=$((TOTAL_NEW + new_completed))

    pct=$((completed * 100 / expected_count))

    # Status indicator
    if [ $completed -eq $expected_count ]; then
        status="✓ DONE    "
    elif [ $new_completed -gt 0 ]; then
        status="⚡ RUNNING "
    elif [ $completed -gt 0 ]; then
        status="🔄 QUEUED  "
    else
        status="⏸  PENDING "
    fi

    printf "%-12s %s %3d/%-3d (%3d%%) [%d new]\n" \
        "$batch_name" "$status" "$completed" "$expected_count" "$pct" "$new_completed"
done

echo "--------------------------------------------------------------------------------"
TOTAL_PCT=$((TOTAL_COMPLETED * 100 / TOTAL_INSTANCES))
printf "%-12s           %3d/%-3d (%3d%%) [%d new]\n" \
    "TOTAL" "$TOTAL_COMPLETED" "$TOTAL_INSTANCES" "$TOTAL_PCT" "$TOTAL_NEW"
echo "================================================================================"
echo ""

# Show timing statistics
echo "📊 Statistics:"
echo "   Elapsed time: ${ELAPSED_MIN} minutes ($((ELAPSED_MIN / 60))h $((ELAPSED_MIN % 60))m)"

if [ $TOTAL_NEW -gt 0 ]; then
    RATE=$(echo "scale=2; $TOTAL_NEW / $ELAPSED_MIN" | bc -l 2>/dev/null || echo "0")
    echo "   Completion rate: $RATE instances/minute"

    REMAINING=$((TOTAL_INSTANCES - TOTAL_COMPLETED))
    if [ $(echo "$RATE > 0" | bc -l 2>/dev/null) -eq 1 ]; then
        ETA_MIN=$(echo "scale=0; $REMAINING / $RATE" | bc -l 2>/dev/null || echo "0")
        ETA_HOURS=$(echo "scale=1; $ETA_MIN / 60" | bc -l 2>/dev/null || echo "0")
        echo "   Remaining: $REMAINING instances"
        echo "   ETA: ~${ETA_HOURS} hours"
    fi
else
    echo "   Status: Waiting for first completions..."
    echo "   Note: First instances take 10-20 minutes to complete"
fi

echo ""

# Show recent batch log activity
if [ -f "$BATCH_LOG" ]; then
    echo "📋 Recent Activity (Batch 1):"
    tail -5 "$BATCH_LOG" | sed 's/^/   /'
fi

echo ""
echo "================================================================================"
echo "Run 'watch -n 30 bash monitor_benchmark.sh' for auto-refresh every 30 seconds"
echo "================================================================================"
