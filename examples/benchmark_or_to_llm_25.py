"""
Benchmark OR-to-LLM strategy 25 times on the three H&M instances used by fullstack_demo.

Instances (matching fullstack_demo app.py exactly):
  - 599580017 (Swimwear), promised_lead_time=0
  - 568601006, promised_lead_time=1
  - 706016001, promised_lead_time=1

Before running, cleans up existing or_to_llm_*.txt logs in each instance folder.
Logs are saved as or_to_llm_1.txt ... or_to_llm_25.txt per instance.
"""

import os
import sys
import subprocess
import re
import json
import argparse
import glob
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
from typing import Dict, List, Tuple, Optional

# Get the current Python executable
PYTHON_EXECUTABLE = sys.executable

# Add project root and examples to path
BASE_DIR = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = BASE_DIR / "examples"
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(EXAMPLES_DIR))

from perfect_score import calculate_perfect_score

# Fullstack demo instance config (must match app.py exactly)
INSTANCE_FOLDERS = ["599580017", "568601006", "706016001"]
INSTANCE_PROMISED_LEAD_TIMES = {
    "599580017": 0,  # Swimwear
    "568601006": 1,
    "706016001": 1,
}

OR_TO_LLM_SCRIPT = BASE_DIR / "examples" / "or_to_llm_csv_demo.py"
SCRIPT_NAME = "or_to_llm"
NUM_RUNS = 25
H_M_INSTANCES_DIR = BASE_DIR / "examples" / "H&M_instances"


def extract_reward_from_output(output: str) -> Optional[float]:
    """Extract total reward from script output."""
    patterns = [
        r">>>\s*Total Reward[^:]*:\s*\$([\d,]+\.?\d*)\s*<<<",
        r"Total Reward[^:]*:\s*\$([\d,]+\.?\d*)",
        r"VM Final Reward:\s*([\d,]+\.?\d*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, output)
        if match:
            try:
                reward_str = match.group(1).replace(",", "")
                return float(reward_str)
            except ValueError:
                continue
    lines = output.split("\n")
    for line in lines:
        if "Total Reward" in line or "total_reward" in line.lower():
            numbers = re.findall(r"[\d,]+\.?\d*", line)
            if numbers:
                try:
                    return float(numbers[-1].replace(",", ""))
                except ValueError:
                    continue
    return None


def cleanup_all_logs(instance_id: str) -> int:
    """Remove all .txt log files in the instance folder (or_to_llm, llm, or, llm_to_or, etc.). Returns count of removed files."""
    instance_dir = H_M_INSTANCES_DIR / instance_id
    if not instance_dir.exists():
        return 0
    pattern = str(instance_dir / "*.txt")
    files = glob.glob(pattern)
    removed = 0
    for f in files:
        try:
            os.remove(f)
            removed += 1
        except OSError:
            pass
    return removed


def run_script(
    script_path: str,
    instance_id: str,
    run_num: int,
    script_name: str,
    promised_lead_time: int,
    max_periods: Optional[int] = None,
) -> Tuple[Optional[float], Optional[str], str]:
    """
    Run or_to_llm_csv_demo.py for a given instance and return (reward, error_message, output).
    Uses same CSV paths and promised_lead_time as fullstack_demo.
    """
    test_file = H_M_INSTANCES_DIR / instance_id / "test.csv"
    train_file = H_M_INSTANCES_DIR / instance_id / "train.csv"

    if not test_file.exists():
        return None, f"Test file not found: {test_file}", ""
    if not train_file.exists():
        return None, f"Train file not found: {train_file}", ""

    cmd = [
        PYTHON_EXECUTABLE,
        str(script_path),
        "--demand-file",
        str(test_file),
        "--promised-lead-time",
        str(promised_lead_time),
        "--real-instance-train",
        str(train_file),
    ]
    if max_periods is not None:
        cmd.extend(["--max-periods", str(max_periods)])

    try:
        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )

        output = result.stdout + result.stderr

        # Save output to log file
        log_filename = f"{script_name}_{run_num}.txt"
        log_path = H_M_INSTANCES_DIR / instance_id / log_filename
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(output)
        except Exception as e:
            output += f"\n[Warning: Could not save log to {log_path}: {str(e)}]"

        reward = extract_reward_from_output(output)

        if reward is None:
            return (
                None,
                f"Could not extract reward from output. Exit code: {result.returncode}",
                output,
            )

        if result.returncode != 0:
            return None, f"Script failed with exit code {result.returncode}", output

        return reward, None, output

    except Exception as e:
        return None, f"Error running script: {str(e)}", ""


def run_single_task(task_info: tuple) -> Tuple[tuple, Tuple]:
    """Wrapper for parallel execution."""
    (
        script_path,
        instance_id,
        run_num,
        script_name,
        promised_lead_time,
        max_periods,
    ) = task_info
    key = (script_path, instance_id, run_num, script_name)
    result = run_script(
        script_path, instance_id, run_num, script_name, promised_lead_time, max_periods
    )
    return key, result


def benchmark_or_to_llm_25(max_periods: Optional[int] = None, max_workers: Optional[int] = None):
    """Run OR-to-LLM 25 times per instance with parallelism."""
    # 1. Clean up all existing logs in the three instance folders
    print("=" * 80)
    print("STEP 1: Cleaning up all existing .txt logs (or_to_llm, llm, or, llm_to_or, etc.)")
    print("=" * 80)
    total_removed = 0
    for instance_id in INSTANCE_FOLDERS:
        removed = cleanup_all_logs(instance_id)
        total_removed += removed
        print(f"  {instance_id}: removed {removed} log(s)")
    print(f"Total removed: {total_removed} log file(s)\n")

    # 2. Verify instances and compute perfect scores
    print("STEP 2: Verifying instances and computing perfect scores (fullstack_demo consistency)")
    print("=" * 80)
    perfect_scores = {}
    for instance_id in INSTANCE_FOLDERS:
        test_file = H_M_INSTANCES_DIR / instance_id / "test.csv"
        train_file = H_M_INSTANCES_DIR / instance_id / "train.csv"
        plt = INSTANCE_PROMISED_LEAD_TIMES[instance_id]
        ok = test_file.exists() and train_file.exists()
        print(f"  {instance_id}: test.csv={test_file.exists()}, train.csv={train_file.exists()}, promised_lead_time={plt} {'OK' if ok else 'MISSING'}")
        if not ok:
            print("Error: Instance files missing. Aborting.")
            return
        try:
            ps_result = calculate_perfect_score(str(test_file))
            perfect_scores[instance_id] = ps_result["_total"]["total_perfect_score"]
            print(f"         Perfect Score: ${perfect_scores[instance_id]:.2f}")
        except Exception as e:
            print(f"         Perfect Score: ERROR - {e}")
            perfect_scores[instance_id] = None
    print()

    # 3. Prepare tasks
    if max_workers is None:
        max_workers = min(6, (os.cpu_count() or 4) * 2)

    all_tasks = []
    for instance_id in INSTANCE_FOLDERS:
        promised_lead_time = INSTANCE_PROMISED_LEAD_TIMES[instance_id]
        for run_num in range(1, NUM_RUNS + 1):
            all_tasks.append(
                (
                    str(OR_TO_LLM_SCRIPT),
                    instance_id,
                    run_num,
                    SCRIPT_NAME,
                    promised_lead_time,
                    max_periods,
                )
            )

    total_tasks = len(all_tasks)
    print("STEP 3: Running OR-to-LLM benchmark")
    print("=" * 80)
    print(f"Instances: {INSTANCE_FOLDERS}")
    print(f"Runs per instance: {NUM_RUNS}")
    print(f"Total runs: {total_tasks}")
    print(f"Parallel workers: {max_workers}")
    if max_periods:
        print(f"Max periods per run: {max_periods}")
    print()

    results = defaultdict(list)
    errors = defaultdict(list)
    completed = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {executor.submit(run_single_task, t): t for t in all_tasks}

        for future in as_completed(future_to_task):
            completed += 1
            task = future_to_task[future]
            _, instance_id, run_num, _, _, _ = task

            try:
                key, (reward, error, output) = future.result()
                if error:
                    print(f"[{instance_id}] Run {run_num}/{NUM_RUNS} ({completed}/{total_tasks}): ERROR: {error}")
                    errors[instance_id].append((run_num, error))
                else:
                    print(f"[{instance_id}] Run {run_num}/{NUM_RUNS} ({completed}/{total_tasks}): Reward: ${reward:.2f} (log saved)")
                    results[instance_id].append(reward)
            except Exception as e:
                print(f"[{instance_id}] Run {run_num}/{NUM_RUNS} ({completed}/{total_tasks}): EXCEPTION: {str(e)}")
                errors[instance_id].append((run_num, f"Exception: {str(e)}"))

    # 4. Summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    print("\nPer-Instance Statistics:")
    print("-" * 110)
    print(
        f"{'Instance':<12} {'Perfect Score':<16} {'Avg Reward':<14} {'Achievement %':<14} {'Std Dev':<12} {'Min':<12} {'Max':<12} {'Runs':<8}"
    )
    print("-" * 110)

    per_instance = {}
    for instance_id in INSTANCE_FOLDERS:
        rewards = results[instance_id]
        ps = perfect_scores.get(instance_id)
        if rewards:
            mean = float(np.mean(rewards))
            std = float(np.std(rewards))
            min_r = float(np.min(rewards))
            max_r = float(np.max(rewards))
            ach_pct = (mean / ps * 100) if ps and ps > 0 else None
            ps_str = f"${ps:.2f}" if ps is not None else "N/A"
            ach_str = f"{ach_pct:.1f}%" if ach_pct is not None else "N/A"
            print(
                f"{instance_id:<12} {ps_str:<16} ${mean:<13.2f} {ach_str:<14} "
                f"${std:<11.2f} ${min_r:<11.2f} ${max_r:<11.2f} {len(rewards):<8}"
            )
            per_instance[instance_id] = {
                "perfect_score": float(ps) if ps is not None else None,
                "rewards": [float(r) for r in rewards],
                "mean": mean,
                "std": std,
                "min": min_r,
                "max": max_r,
                "count": len(rewards),
                "achievement_pct": float(ach_pct) if ach_pct is not None else None,
            }
        else:
            ps_str = f"${ps:.2f}" if ps is not None else "N/A"
            print(
                f"{instance_id:<12} {ps_str:<16} {'N/A':<14} {'N/A':<14} {'N/A':<12} {'N/A':<12} {'N/A':<12} {0:<8}"
            )
            per_instance[instance_id] = {
                "perfect_score": float(ps) if ps is not None else None,
                "rewards": [],
                "mean": None,
                "std": None,
                "min": None,
                "max": None,
                "count": 0,
                "achievement_pct": None,
            }

    if errors:
        print("\nErrors:")
        for instance_id in INSTANCE_FOLDERS:
            if errors[instance_id]:
                print(f"  {instance_id}:")
                for run_num, err in errors[instance_id]:
                    print(f"    Run {run_num}: {err}")

    # Overall
    all_rewards = []
    total_perfect = 0.0
    total_mean_reward = 0.0
    for instance_id in INSTANCE_FOLDERS:
        r = results[instance_id]
        all_rewards.extend(r)
        ps = perfect_scores.get(instance_id)
        if ps is not None:
            total_perfect += ps
        if r:
            total_mean_reward += np.mean(r)
    if all_rewards:
        print("\nOverall (all instances combined):")
        overall_mean = np.mean(all_rewards)
        print(
            f"  Mean: ${overall_mean:.2f}, Std: ${np.std(all_rewards):.2f}, "
            f"Min: ${np.min(all_rewards):.2f}, Max: ${np.max(all_rewards):.2f}"
        )
        if total_perfect > 0:
            overall_ach = total_mean_reward / total_perfect * 100
            print(f"  Total Perfect Score: ${total_perfect:.2f}, Overall Achievement: {overall_ach:.1f}%")

    # Save JSON
    output_file = BASE_DIR / "examples" / "benchmark_or_to_llm_25_results.json"
    detailed = {
        "instances": INSTANCE_FOLDERS,
        "num_runs_per_instance": NUM_RUNS,
        "promised_lead_times": INSTANCE_PROMISED_LEAD_TIMES,
        "perfect_scores": perfect_scores,
        "per_instance": per_instance,
        "errors": {k: [{"run": r, "error": e} for r, e in v] for k, v in errors.items() if v},
    }
    with open(output_file, "w") as f:
        json.dump(detailed, f, indent=2)
    print(f"\nDetailed results saved to: {output_file}")
    print("=" * 80)


def retry_failed_runs(max_periods: Optional[int] = None, max_workers: Optional[int] = None):
    """Re-run only the failed runs from the last benchmark, update logs and results JSON."""
    results_file = BASE_DIR / "examples" / "benchmark_or_to_llm_25_results.json"
    if not results_file.exists():
        print("Error: benchmark_or_to_llm_25_results.json not found. Run full benchmark first.")
        return

    with open(results_file, "r") as f:
        data = json.load(f)

    errors = data.get("errors", {})
    failed_tasks = []
    for instance_id, err_list in errors.items():
        for item in err_list:
            failed_tasks.append((instance_id, item["run"]))

    if not failed_tasks:
        print("No failed runs to retry.")
        return

    if max_workers is None:
        max_workers = min(6, (os.cpu_count() or 4) * 2)

    print("=" * 80)
    print("RETRY FAILED RUNS")
    print("=" * 80)
    print(f"Failed runs to retry: {len(failed_tasks)}")
    for instance_id, run_num in sorted(failed_tasks):
        print(f"  {instance_id} run {run_num}")
    print(f"Parallel workers: {max_workers}\n")

    tasks = []
    for instance_id, run_num in failed_tasks:
        promised_lead_time = INSTANCE_PROMISED_LEAD_TIMES[instance_id]
        tasks.append(
            (
                str(OR_TO_LLM_SCRIPT),
                instance_id,
                run_num,
                SCRIPT_NAME,
                promised_lead_time,
                max_periods,
            )
        )

    results = defaultdict(list)
    still_failed = defaultdict(list)
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {executor.submit(run_single_task, t): t for t in tasks}
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            _, instance_id, run_num, _, _, _ = task
            try:
                _, (reward, error, _) = future.result()
                if error:
                    print(f"[{instance_id}] Run {run_num}: ERROR: {error}")
                    still_failed[instance_id].append((run_num, error))
                else:
                    print(f"[{instance_id}] Run {run_num}: Reward: ${reward:.2f} (log saved)")
                    results[instance_id].append((run_num, reward))
            except Exception as e:
                print(f"[{instance_id}] Run {run_num}: EXCEPTION: {e}")
                still_failed[instance_id].append((run_num, str(e)))

    perfect_scores = data.get("perfect_scores", {})
    per_instance = data.get("per_instance", {})

    for instance_id in INSTANCE_FOLDERS:
        existing_rewards = list(per_instance.get(instance_id, {}).get("rewards", []))
        new_rewards = [r for _, r in sorted(results[instance_id], key=lambda x: x[0])]
        combined = existing_rewards + new_rewards

        remaining_errors = [{"run": r, "error": e} for r, e in still_failed[instance_id]]

        ps = perfect_scores.get(instance_id)
        if combined:
            mean = float(np.mean(combined))
            std = float(np.std(combined))
            min_r = float(np.min(combined))
            max_r = float(np.max(combined))
            ach = (mean / ps * 100) if ps and ps > 0 else None
        else:
            mean = std = min_r = max_r = ach = None

        per_instance[instance_id] = {
            "perfect_score": float(ps) if ps is not None else None,
            "rewards": [float(r) for r in combined],
            "mean": mean,
            "std": std,
            "min": min_r,
            "max": max_r,
            "count": len(combined),
            "achievement_pct": float(ach) if ach is not None else None,
        }

    data["per_instance"] = per_instance
    data["errors"] = {
        inst: [{"run": r, "error": e} for r, e in errs]
        for inst, errs in still_failed.items()
        if errs
    }

    with open(results_file, "w") as f:
        json.dump(data, f, indent=2)

    print("\n" + "=" * 80)
    print("UPDATED RESULTS SUMMARY")
    print("=" * 80)
    print(
        f"{'Instance':<12} {'Perfect Score':<16} {'Avg Reward':<14} {'Achievement %':<14} {'Runs':<8}"
    )
    print("-" * 70)
    for instance_id in INSTANCE_FOLDERS:
        pi = per_instance[instance_id]
        ps = pi.get("perfect_score")
        mean = pi.get("mean")
        ach = pi.get("achievement_pct")
        count = pi.get("count", 0)
        ps_str = f"${ps:.2f}" if ps is not None else "N/A"
        mean_str = f"${mean:.2f}" if mean is not None else "N/A"
        ach_str = f"{ach:.1f}%" if ach is not None else "N/A"
        print(f"{instance_id:<12} {ps_str:<16} {mean_str:<14} {ach_str:<14} {count:<8}")
    if data["errors"]:
        print("\nRemaining errors:")
        for instance_id, err_list in data["errors"].items():
            for e in err_list:
                print(f"  {instance_id} run {e['run']}: {e['error']}")
    print(f"\nUpdated: {results_file}")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark OR-to-LLM 25 times on fullstack demo's three H&M instances"
    )
    parser.add_argument(
        "--max-periods",
        type=int,
        default=None,
        help="Maximum periods per run (default: all from test.csv)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Parallel workers (default: min(6, CPU*2))",
    )
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Re-run only failed runs from last benchmark, update logs and results JSON",
    )
    args = parser.parse_args()

    if args.retry_failed:
        retry_failed_runs(max_periods=args.max_periods, max_workers=args.max_workers)
    else:
        benchmark_or_to_llm_25(max_periods=args.max_periods, max_workers=args.max_workers)
