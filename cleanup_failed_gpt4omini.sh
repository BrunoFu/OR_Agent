#!/bin/bash

# Script to clean up failed gpt-4o-mini results (incomplete benchmarks with errors)
# These results only have 2/5 strategies completed (or and perfect_score)
# All LLM strategies (llm, llm_to_or, or_to_llm) failed

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║     Cleanup Failed gpt-4o-mini Results                               ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

cd /shared/share_malatown/OR-Agent-GPT5mini-benchmark

# Find all benchmark_results.json files with model="gpt-4o-mini" and errors
echo "Searching for failed gpt-4o-mini results..."
echo ""

failed_count=0
total_checked=0

for result_file in $(find examples/benchmark -name "benchmark_results.json" -type f); do
    total_checked=$((total_checked + 1))

    # Check if this result uses gpt-4o-mini and has errors
    model=$(cat "$result_file" | jq -r '.model' 2>/dev/null)
    has_llm_error=$(cat "$result_file" | jq -r '.errors.llm | length > 0' 2>/dev/null)

    if [ "$model" = "gpt-4o-mini" ] && [ "$has_llm_error" = "true" ]; then
        instance_dir=$(dirname "$result_file")
        instance_name=$(basename "$instance_dir")

        echo "Removing failed result: $instance_name"
        echo "  Path: $result_file"

        # Remove the benchmark_results.json file
        rm -f "$result_file"

        # Also remove the individual output files from the failed run
        rm -f "$instance_dir"/llm_*.txt 2>/dev/null
        rm -f "$instance_dir"/or_to_llm_*.txt 2>/dev/null
        rm -f "$instance_dir"/llm_to_or_*.txt 2>/dev/null

        failed_count=$((failed_count + 1))
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Cleanup Summary:"
echo "  Total results checked: $total_checked"
echo "  Failed gpt-4o-mini results removed: $failed_count"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "These instances will be re-run with openai/gpt-5-mini (OpenRouter)"
echo "when you restart the benchmark with --skip-completed flag."
echo ""
