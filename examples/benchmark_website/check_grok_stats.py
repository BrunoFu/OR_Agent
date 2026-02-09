"""Check Grok 4.1 Fast statistics with and without negative value truncation."""
import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent.parent
BENCH_DIR = ROOT / "examples" / "grok-4.1-fast_bench"

METHOD_LABELS = {
    "or": "OR",
    "llm": "LLM",
    "llm_to_or": "LLM→OR",
    "or_to_llm": "OR→LLM",
}

def collect_ratios():
    """Collect all ratio_to_perfect values for each method."""
    methods = {
        "or": [],
        "llm": [],
        "llm_to_or": [],
        "or_to_llm": [],
    }
    
    json_paths = list(BENCH_DIR.rglob("benchmark_results.json"))
    print(f"Found {len(json_paths)} benchmark result files")
    
    for path in json_paths:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        results = data.get("results", {})
        for method, res in results.items():
            if method == "perfect_score":
                continue
            if method not in methods:
                continue
            
            ratio = res.get("ratio_to_perfect")
            if ratio is not None:
                methods[method].append(ratio)
    
    return methods

def main():
    """Compare statistics with and without truncation."""
    methods = collect_ratios()
    
    print("\n" + "="*70)
    print("Grok 4.1 Fast Statistics Comparison")
    print("="*70)
    
    print("\n[Current Method] (includes negative values):")
    print("-" * 70)
    print(f"{'Method':<15} {'Mean':<12} {'Min':<12} {'Max':<12} {'Count':<10} {'Negative Count':<15}")
    print("-" * 70)
    
    current_means = {}
    for method_id, ratios in methods.items():
        if not ratios:
            continue
        
        mean_val = mean(ratios)
        min_val = min(ratios)
        max_val = max(ratios)
        negative_count = sum(1 for r in ratios if r < 0)
        current_means[method_id] = mean_val
        
        print(f"{METHOD_LABELS.get(method_id, method_id):<15} "
              f"{mean_val:<12.4f} "
              f"{min_val:<12.4f} "
              f"{max_val:<12.4f} "
              f"{len(ratios):<10} "
              f"{negative_count:<15}")
    
    print("\n[Truncated Method] (negative values set to 0):")
    print("-" * 70)
    print(f"{'Method':<15} {'Mean':<12} {'Min':<12} {'Max':<12} {'Count':<10} {'Truncated Count':<15}")
    print("-" * 70)
    
    truncated_means = {}
    for method_id, ratios in methods.items():
        if not ratios:
            continue
        
        truncated = [max(0, r) for r in ratios]
        mean_val = mean(truncated)
        min_val = min(truncated)
        max_val = max(truncated)
        truncated_count = sum(1 for r in ratios if r < 0)
        truncated_means[method_id] = mean_val
        
        print(f"{METHOD_LABELS.get(method_id, method_id):<15} "
              f"{mean_val:<12.4f} "
              f"{min_val:<12.4f} "
              f"{max_val:<12.4f} "
              f"{len(truncated):<10} "
              f"{truncated_count:<15}")
    
    print("\n[Comparison with Chart Data]:")
    print("-" * 70)
    chart_data = {
        "or": 0.445,
        "llm": 0.459,
        "or_to_llm": 0.514,
        "llm_to_or": 0.493,
    }
    
    print(f"{'Method':<15} {'Chart':<12} {'Current':<12} {'Truncated':<12} {'Diff (Current)':<15} {'Diff (Truncated)':<15}")
    print("-" * 70)
    
    for method_id in ["or", "llm", "or_to_llm", "llm_to_or"]:
        chart_val = chart_data.get(method_id, 0)
        current_val = current_means.get(method_id, 0)
        truncated_val = truncated_means.get(method_id, 0)
        
        diff_current = abs(chart_val - current_val)
        diff_truncated = abs(chart_val - truncated_val)
        
        match_indicator_current = "[MATCH]" if diff_current < 0.01 else "[NO]"
        match_indicator_truncated = "[MATCH]" if diff_truncated < 0.01 else "[NO]"
        
        print(f"{METHOD_LABELS.get(method_id, method_id):<15} "
              f"{chart_val:<12.4f} "
              f"{current_val:<12.4f} "
              f"{truncated_val:<12.4f} "
              f"{diff_current:<15.4f} {match_indicator_current:<8} "
              f"{diff_truncated:<15.4f} {match_indicator_truncated}")
    
    print("\n" + "="*70)
    print("Summary:")
    print("="*70)
    
    total_diff_current = sum(abs(chart_data.get(m, 0) - current_means.get(m, 0)) 
                             for m in chart_data.keys())
    total_diff_truncated = sum(abs(chart_data.get(m, 0) - truncated_means.get(m, 0)) 
                               for m in chart_data.keys())
    
    print(f"Total absolute difference (Current):   {total_diff_current:.4f}")
    print(f"Total absolute difference (Truncated):  {total_diff_truncated:.4f}")
    
    if total_diff_truncated < total_diff_current:
        print("\n[RESULT] Truncated method matches chart data better!")
    else:
        print("\n[RESULT] Current method (with negatives) matches chart data better!")
    
    # Show some examples of negative values
    print("\n[Sample Negative Values Found]:")
    print("-" * 70)
    sample_count = 0
    for method_id, ratios in methods.items():
        negatives = [r for r in ratios if r < 0]
        if negatives and sample_count < 5:
            print(f"{METHOD_LABELS.get(method_id, method_id)}: {len(negatives)} negative values")
            print(f"  Examples: {negatives[:3]}")
            sample_count += 1

if __name__ == "__main__":
    main()
