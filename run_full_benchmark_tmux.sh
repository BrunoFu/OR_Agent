#!/bin/bash

# Run complete benchmark suite (1,320 instances) with improved prompt
# Usage: bash run_full_benchmark_tmux.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source .venv/bin/activate

# Configuration
SESSION_NAME="gpt5mini_improved_full"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="benchmark_logs_improved_${TIMESTAMP}"
mkdir -p "$LOG_DIR"

echo "=========================================="
echo "GPT-5-MINI IMPROVED PROMPT - FULL BENCHMARK"
echo "=========================================="
echo "Session: $SESSION_NAME"
echo "Log directory: $LOG_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""

# Find all test instances
echo "Discovering instances..."
INSTANCES=($(find examples/benchmark/synthetic_trajectory/lead_time_stochastic -name "test.csv" | sort))
TOTAL=${#INSTANCES[@]}

echo "Found $TOTAL instances to run"
echo ""

# Kill existing tmux session if it exists
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

# Create new tmux session
echo "Creating tmux session: $SESSION_NAME"
tmux new-session -d -s "$SESSION_NAME"

# Set up the main window
tmux rename-window -t "$SESSION_NAME":0 "monitor"
tmux send-keys -t "$SESSION_NAME":0 "cd $SCRIPT_DIR" C-m
tmux send-keys -t "$SESSION_NAME":0 "source .venv/bin/activate" C-m

# Create function to run a single instance
cat > /tmp/run_single_instance_improved.sh << 'RUNSCRIPT'
#!/bin/bash
INSTANCE_DIR="$1"
LOG_DIR="$2"

# Extract instance info
PROBLEM=$(echo "$INSTANCE_DIR" | grep -oP 'p\d+_[^/]+')
VARIANT=$(echo "$INSTANCE_DIR" | grep -oP 'v\d+_[^/]+')
REPLICA=$(basename "$INSTANCE_DIR")

LOG_FILE="$LOG_DIR/${PROBLEM}_${VARIANT}_${REPLICA}.log"
RESULT_FILE="$LOG_DIR/${PROBLEM}_${VARIANT}_${REPLICA}.result"

echo "[$(date '+%H:%M:%S')] Starting: $PROBLEM/$VARIANT/$REPLICA" >> "$LOG_DIR/progress.log"

# Run the benchmark
python examples/or_to_llm_csv_demo.py \
    --demand-file "${INSTANCE_DIR}/test.csv" \
    --real-instance-train "${INSTANCE_DIR}/train.csv" \
    --promised-lead-time 2 \
    --model "openai/gpt-5-mini" \
    > "$LOG_FILE" 2>&1

# Extract reward
REWARD=$(grep -oP "Total Reward.*: \$\K[0-9.-]+" "$LOG_FILE" | tail -1)
echo "$PROBLEM,$VARIANT,$REPLICA,$REWARD" >> "$LOG_DIR/results.csv"
echo "$PROBLEM/$VARIANT/$REPLICA: $REWARD" > "$RESULT_FILE"

echo "[$(date '+%H:%M:%S')] Completed: $PROBLEM/$VARIANT/$REPLICA (Reward: $REWARD)" >> "$LOG_DIR/progress.log"
RUNSCRIPT

chmod +x /tmp/run_single_instance_improved.sh

# Initialize results CSV
echo "Problem,Variant,Replica,Reward" > "$LOG_DIR/results.csv"
echo "" > "$LOG_DIR/progress.log"

# Create worker windows (run 10 in parallel)
NUM_WORKERS=10
echo "Creating $NUM_WORKERS worker windows..."

for i in $(seq 0 $((NUM_WORKERS - 1))); do
    window_name="worker_$i"
    tmux new-window -t "$SESSION_NAME" -n "$window_name"
    tmux send-keys -t "$SESSION_NAME":"$window_name" "cd $SCRIPT_DIR" C-m
    tmux send-keys -t "$SESSION_NAME":"$window_name" "source .venv/bin/activate" C-m
done

# Distribute instances across workers
echo "Distributing $TOTAL instances across $NUM_WORKERS workers..."
worker_id=0
instance_count=0

for instance in "${INSTANCES[@]}"; do
    instance_dir=$(dirname "$instance")
    window_name="worker_$worker_id"

    # Send command to worker
    tmux send-keys -t "$SESSION_NAME":"$window_name" \
        "bash /tmp/run_single_instance_improved.sh '$instance_dir' '$LOG_DIR' && echo 'Worker $worker_id ready'" C-m

    ((instance_count++))
    ((worker_id++))

    # Wrap around to first worker
    if [ $worker_id -ge $NUM_WORKERS ]; then
        worker_id=0
    fi

    # Print progress
    if [ $((instance_count % 100)) -eq 0 ]; then
        echo "  Queued: $instance_count/$TOTAL instances..."
    fi
done

echo ""
echo "All instances queued!"
echo ""

# Set up monitoring window
tmux send-keys -t "$SESSION_NAME":0 "watch -n 10 'echo \"=== Benchmark Progress ===\" && echo \"\" && wc -l $LOG_DIR/results.csv | awk \"{print \\$1-1 \\\"/\\\" $TOTAL \\\" instances completed\\\"}\" && echo \"\" && tail -20 $LOG_DIR/progress.log'" C-m

# Create summary script
cat > "$LOG_DIR/generate_summary.sh" << 'SUMMARYSCRIPT'
#!/bin/bash
LOG_DIR=$(dirname "$0")

echo "=========================================="
echo "BENCHMARK SUMMARY"
echo "=========================================="
echo ""

# Count completed
completed=$(wc -l < "$LOG_DIR/results.csv")
((completed--)) # Subtract header

echo "Completed: $completed instances"
echo ""

if [ $completed -gt 0 ]; then
    echo "=== Top 10 Results ==="
    tail -n +2 "$LOG_DIR/results.csv" | sort -t',' -k4 -rn | head -10 | \
        awk -F',' '{printf "%-30s %-20s %8.1f\n", $1, $2, $4}'

    echo ""
    echo "=== Problem Type Averages ==="
    tail -n +2 "$LOG_DIR/results.csv" | \
        awk -F',' '{sum[$1]+=$4; count[$1]++} END {for (p in sum) printf "%-30s %8.1f\n", p, sum[p]/count[p]}' | \
        sort
fi
SUMMARYSCRIPT

chmod +x "$LOG_DIR/generate_summary.sh"

echo "=========================================="
echo "BENCHMARK STARTED"
echo "=========================================="
echo ""
echo "To monitor progress:"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "To detach from tmux:"
echo "  Press Ctrl+B, then D"
echo ""
echo "To view summary:"
echo "  bash $LOG_DIR/generate_summary.sh"
echo ""
echo "To generate final comparison report:"
echo "  bash compare_with_original.sh $LOG_DIR"
echo ""
echo "Log directory: $LOG_DIR"
echo "=========================================="

# Attach to tmux session
tmux attach -t "$SESSION_NAME"
