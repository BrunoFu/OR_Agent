#!/bin/bash

# Script to check the status of all benchmark tmux sessions

echo "=========================================="
echo "OR-Agent Benchmark Status Checker"
echo "=========================================="
echo ""
echo "Active tmux sessions:"
tmux list-sessions 2>&1 || echo "No active tmux sessions found"
echo ""
echo "=========================================="
echo ""

# Array of session names
declare -a SESSIONS=(
    "synthetic-L0"
    "synthetic-L4"
    "synthetic-Lstoch"
    "real-L0"
    "real-L4"
    "real-Lstoch"
)

# Check each session
for session in "${SESSIONS[@]}"; do
    echo "-------------------------------------------"
    echo "Session: $session"
    echo "-------------------------------------------"

    # Check if session exists
    if tmux has-session -t "$session" 2>/dev/null; then
        echo "Status: RUNNING"
        echo ""
        echo "Last 20 lines of output:"
        tmux capture-pane -pt "$session" -S -20 2>&1 | tail -20
    else
        echo "Status: NOT RUNNING"
    fi
    echo ""
done

echo "=========================================="
echo "Commands:"
echo "  - Attach to session: tmux attach-session -t <session-name>"
echo "  - Kill session: tmux kill-session -t <session-name>"
echo "  - Kill all: tmux kill-server"
echo "=========================================="
