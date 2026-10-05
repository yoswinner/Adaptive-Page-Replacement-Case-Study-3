"""
Textbook Validation Experiment Runner.
Course: BCSE303L - Operating Systems
Students:
  1. 24BCE0702 - Yash Pradhan
  2. 24BCE0714 - Anjini Pandey

Validates baseline algorithms against standard textbook reference string:
7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1
Capacity: 3 frames.
"""

import os
import sys
import csv

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.fifo import run_fifo
from src.lru import run_lru
from src.optimal import run_optimal
from src.clock import run_clock
from src.lfu import run_lfu

def run_textbook_validation():
    ref_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    capacity = 3

    expected = {
        "FIFO": 15,
        "LRU": 12,
        "Optimal": 9,
        "Clock": 14,   # Hand-traced with documented semantics (hand advances on fill, not on hit)
        "LFU": 13      # Hand-traced with documented FIFO (oldest-arrival) tie-break
    }

    results = []

    # Run FIFO
    res_fifo = run_fifo(ref_string, capacity, workload_type="textbook_validation")
    status_fifo = "PASS" if res_fifo.page_faults == expected["FIFO"] else "FAIL"
    results.append({
        "algorithm": "FIFO",
        "faults": res_fifo.page_faults,
        "hits": res_fifo.page_hits,
        "hit_ratio": res_fifo.hit_ratio,
        "expected_faults": expected["FIFO"],
        "status": status_fifo,
        "notes": "Strict queue-based eviction"
    })

    # Run LRU
    res_lru = run_lru(ref_string, capacity, workload_type="textbook_validation")
    status_lru = "PASS" if res_lru.page_faults == expected["LRU"] else "FAIL"
    results.append({
        "algorithm": "LRU",
        "faults": res_lru.page_faults,
        "hits": res_lru.page_hits,
        "hit_ratio": res_lru.hit_ratio,
        "expected_faults": expected["LRU"],
        "status": status_lru,
        "notes": "OrderedDict recency order"
    })

    # Run Optimal
    res_opt = run_optimal(ref_string, capacity, workload_type="textbook_validation")
    status_opt = "PASS" if res_opt.page_faults == expected["Optimal"] else "FAIL"
    results.append({
        "algorithm": "Optimal",
        "faults": res_opt.page_faults,
        "hits": res_opt.page_hits,
        "hit_ratio": res_opt.hit_ratio,
        "expected_faults": expected["Optimal"],
        "status": status_opt,
        "notes": "Belady's MIN farthest-future lookahead"
    })

    # Run Clock
    res_clock = run_clock(ref_string, capacity, workload_type="textbook_validation")
    results.append({
        "algorithm": "Clock",
        "faults": res_clock.page_faults,
        "hits": res_clock.page_hits,
        "hit_ratio": res_clock.hit_ratio,
        "expected_faults": expected["Clock"],
        "status": "PASS" if res_clock.page_faults == expected["Clock"] else "FAIL",
        "notes": "Hand-traced expectation; second-chance circular hand, ref bit cleared on sweep"
    })

    # Run LFU
    res_lfu = run_lfu(ref_string, capacity, workload_type="textbook_validation")
    results.append({
        "algorithm": "LFU",
        "faults": res_lfu.page_faults,
        "hits": res_lfu.page_hits,
        "hit_ratio": res_lfu.hit_ratio,
        "expected_faults": expected["LFU"],
        "status": "PASS" if res_lfu.page_faults == expected["LFU"] else "FAIL",
        "notes": "Hand-traced expectation; frequency count with FIFO tie-breaker for identical lowest frequency"
    })

    # Save to results/validation_results.csv
    results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
    os.makedirs(results_dir, exist_ok=True)
    csv_path = os.path.join(results_dir, "validation_results.csv")

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["algorithm", "faults", "hits", "hit_ratio", "expected_faults", "status", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # Save also to report/validation_table.csv
    report_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "report"))
    os.makedirs(report_dir, exist_ok=True)
    report_csv_path = os.path.join(report_dir, "validation_table.csv")
    with open(report_csv_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["algorithm", "faults", "hits", "hit_ratio", "expected_faults", "status", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print("=" * 70)
    print("TEXTBOOK VALIDATION RESULTS (String length: 20, Frames: 3)")
    print("=" * 70)
    print(f"{'Algorithm':<10} | {'Faults':<7} | {'Hits':<5} | {'Hit Ratio':<10} | {'Expected':<9} | {'Status':<6}")
    print("-" * 70)
    all_passed = True
    for r in results:
        print(f"{r['algorithm']:<10} | {r['faults']:<7} | {r['hits']:<5} | {r['hit_ratio']*100:>6.2f}%    | {str(r['expected_faults']):<9} | {r['status']:<6}")
        if r['status'] != 'PASS':
            all_passed = False
    print("=" * 70)

    if not all_passed:
        raise ValueError("Textbook validation failed for one or more baseline algorithms!")

    return results

if __name__ == "__main__":
    run_textbook_validation()
