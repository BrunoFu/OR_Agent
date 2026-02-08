# OR-Agent GPT5-mini Benchmark Run Guide

## Setup Complete! ✓

All 6 benchmark batches are now running in separate tmux sessions with authentication configured.

## Batch Configuration

Each batch is configured with:
- **Parallel instances**: 3 (3 instances run concurrently)
- **Skip completed**: YES (finished instances are automatically skipped)
- **Workers per instance**: 3 (default)

### Running Batches

| Session Name | Description | Instances | Base Directory |
|-------------|-------------|-----------|----------------|
| `synthetic-L0` | Synthetic L=0 | 240 | `examples/benchmark/synthetic_trajectory/lead_time_0` |
| `synthetic-L4` | Synthetic L=4 | 240 | `examples/benchmark/synthetic_trajectory/lead_time_4` |
| `synthetic-Lstoch` | Synthetic L=stochastic | 240 | `examples/benchmark/synthetic_trajectory/lead_time_stochastic` |
| `real-L0` | Real L=0 | 200 | `examples/benchmark/real_trajectory/lead_time_0` |
| `real-L4` | Real L=4 | 200 | `examples/benchmark/real_trajectory/lead_time_4` |
| `real-Lstoch` | Real L=stochastic | 200 | `examples/benchmark/real_trajectory/lead_time_stochastic` |

**Total: 1,320 instances across all batches**

## Quick Commands

### Check Status of All Sessions
```bash
./check_benchmark_status.sh
```

### View Active Sessions
```bash
tmux list-sessions
```

### Attach to a Specific Session (to watch live progress)
```bash
# Attach to synthetic-L0
tmux attach-session -t synthetic-L0

# Detach without killing: Press Ctrl+B then D
```

### Check Progress from Command Line
```bash
# View last 50 lines of a session
tmux capture-pane -pt synthetic-L0 -S -50

# View last 50 lines of real-L0
tmux capture-pane -pt real-L0 -S -50
```

### Kill a Specific Session
```bash
tmux kill-session -t synthetic-L0
```

### Kill All Sessions
```bash
tmux kill-server
```

## Monitoring Progress

### Check Logs for a Specific Batch
Each batch creates log files in its base directory:
```bash
# Synthetic L=0 logs
ls -lh examples/benchmark/synthetic_trajectory/lead_time_0/batch_log_*.txt
ls -lh examples/benchmark/synthetic_trajectory/lead_time_0/batch_summary_*.json

# Real L=0 logs
ls -lh examples/benchmark/real_trajectory/lead_time_0/batch_log_*.txt
ls -lh examples/benchmark/real_trajectory/lead_time_0/batch_summary_*.json
```

### View Latest Log
```bash
# View latest batch log for synthetic L=0
tail -f examples/benchmark/synthetic_trajectory/lead_time_0/batch_log_*.txt

# View latest batch log for real L=0
tail -f examples/benchmark/real_trajectory/lead_time_0/batch_log_*.txt
```

### Check Results Summary
```bash
# Check the latest summary JSON
cat examples/benchmark/real_trajectory/lead_time_0/batch_summary_*.json | jq
```

## Re-running After Completion

If you need to re-run specific batches:

### Re-run a Single Batch
```bash
cd /shared/share_malatown/OR-Agent-GPT5mini-benchmark

# Re-run with skip-completed (resume)
export OPENROUTER_API_KEY="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"
uv run python examples/run_batch_benchmark.py \
    --base-dir examples/benchmark/real_trajectory/lead_time_0 \
    --parallel-instances 3 \
    --skip-completed

# Force re-run all instances (ignore completed)
uv run python examples/run_batch_benchmark.py \
    --base-dir examples/benchmark/real_trajectory/lead_time_0 \
    --parallel-instances 3 \
    --force
```

### Re-launch All Batches in tmux
```bash
# Kill existing sessions first
tmux kill-server

# Re-launch all
./launch_all_benchmarks.sh
```

## Expected Runtime

With 3 parallel instances:
- **Synthetic batches** (240 instances each): ~hours (if not all completed)
- **Real batches** (200 instances each): ~hours (if not all completed)

**Note**: Instances that are already completed will be skipped automatically with `--skip-completed` flag.

## Directory Structure

```
OR-Agent-GPT5mini-benchmark/
├── examples/
│   ├── benchmark/
│   │   ├── synthetic_trajectory/
│   │   │   ├── lead_time_0/          # 240 instances
│   │   │   ├── lead_time_4/          # 240 instances
│   │   │   └── lead_time_stochastic/ # 240 instances
│   │   └── real_trajectory/
│   │       ├── lead_time_0/          # 200 instances
│   │       ├── lead_time_4/          # 200 instances
│   │       └── lead_time_stochastic/ # 200 instances
│   └── run_batch_benchmark.py
├── launch_all_benchmarks.sh          # Launch all batches
├── check_benchmark_status.sh         # Check status
└── BENCHMARK_RUN_GUIDE.md           # This file
```

## Troubleshooting

### Session Not Found
```bash
# Check if session exists
tmux has-session -t synthetic-L0 && echo "EXISTS" || echo "NOT FOUND"
```

### Re-authenticate
If you get API errors, check the environment variable:
```bash
echo $OPENROUTER_API_KEY
```

### View Errors
```bash
# Check for failed instances in summary
cat examples/benchmark/real_trajectory/lead_time_0/batch_summary_*.json | jq '.failed'
```

## Notes

- **All sessions are detached by default** - they run in the background
- **Progress is logged** to batch_log_*.txt files in each base directory
- **Results are saved** to batch_summary_*.json files
- **Individual instance results** are saved in each instance's directory as `benchmark_results.json`
- **The --skip-completed flag ensures** that finished instances are not re-run

## Contact & Issues

For issues with the benchmark runner, check the logs or attach to the tmux session to see real-time output.
