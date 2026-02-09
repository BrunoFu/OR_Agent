#!/bin/bash

# Compare improved results with original benchmark
# Usage: bash compare_with_original.sh <improved_log_dir>

if [ $# -ne 1 ]; then
    echo "Usage: $0 <improved_log_dir>"
    exit 1
fi

IMPROVED_DIR="$1"
ORIGINAL_DIR="examples/benchmark_ORIGINAL_20260209"

if [ ! -d "$IMPROVED_DIR" ]; then
    echo "Error: Improved results directory not found: $IMPROVED_DIR"
    exit 1
fi

if [ ! -d "$ORIGINAL_DIR" ]; then
    echo "Error: Original results directory not found: $ORIGINAL_DIR"
    echo "Make sure you backed up the original results first!"
    exit 1
fi

OUTPUT_FILE="$IMPROVED_DIR/comparison_report.txt"

echo "=========================================="
echo "COMPARISON: ORIGINAL vs IMPROVED PROMPT"
echo "=========================================="
echo ""

# Extract results from improved runs
echo "Extracting improved results..."
python3 << 'PYTHON_SCRIPT'
import json
import csv
import os
import sys
from pathlib import Path
from collections import defaultdict

improved_dir = sys.argv[1]
original_dir = sys.argv[2]

# Read improved results from CSV
improved = {}
results_csv = f"{improved_dir}/results.csv"

if os.path.exists(results_csv):
    with open(results_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row['Problem']}/{row['Variant']}/{row['Replica']}"
            improved[key] = float(row['Reward']) if row['Reward'] else 0.0

# Read original results from benchmark_results.json files
original = {}
for json_file in Path(original_dir).rglob("benchmark_results.json"):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Extract path components
        rel_path = json_file.relative_to(original_dir)
        parts = str(rel_path).split('/')

        # Find problem, variant, replica
        problem = next((p for p in parts if p.startswith('p')), None)
        variant = next((p for p in parts if p.startswith('v')), None)
        replica = next((p for p in parts if p.startswith('r')), None)

        if problem and variant and replica:
            key = f"{problem}/{variant}/{replica}"
            original[key] = data['results']['or_to_llm']['mean']
    except:
        continue

# Generate comparison
print("="*80)
print(f"{'Instance':<50} {'Original':<12} {'Improved':<12} {'Change':<12} {'%':<8}")
print("-"*80)

total_orig = 0
total_impr = 0
count = 0
improvements = []

for key in sorted(set(list(original.keys()) + list(improved.keys()))):
    orig = original.get(key, 0)
    impr = improved.get(key, 0)

    if orig > 0 and impr > 0:
        change = impr - orig
        pct = (change / orig * 100) if orig != 0 else 0

        total_orig += orig
        total_impr += impr
        count += 1
        improvements.append(pct)

        symbol = "✓" if change > 0 else "✗" if change < 0 else "="
        print(f"{key:<50} {orig:>10.1f} {impr:>10.1f} {change:>+10.1f} {pct:>+6.1f}% {symbol}")

print("-"*80)

if count > 0:
    total_change = total_impr - total_orig
    total_pct = (total_change / total_orig * 100) if total_orig != 0 else 0
    avg_impr = sum(improvements) / len(improvements)

    print(f"{'TOTAL':<50} {total_orig:>10.1f} {total_impr:>10.1f} {total_change:>+10.1f} {total_pct:>+6.1f}%")
    print(f"{'AVERAGE PER INSTANCE':<50} {'':<12} {'':<12} {'':<12} {avg_impr:>+6.1f}%")
    print()
    print(f"Instances compared: {count}")
    print(f"Instances improved: {sum(1 for x in improvements if x > 0)}")
    print(f"Instances worse: {sum(1 for x in improvements if x < 0)}")
    print(f"Instances unchanged: {sum(1 for x in improvements if x == 0)}")
else:
    print("No instances to compare yet")

print("="*80)

PYTHON_SCRIPT "$IMPROVED_DIR" "$ORIGINAL_DIR" | tee "$OUTPUT_FILE"

echo ""
echo "Comparison report saved to: $OUTPUT_FILE"
