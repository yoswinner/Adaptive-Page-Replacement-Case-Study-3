"""
Comprehensive Experiment Matrix Runner.
Course: BCSE303L - Operating Systems
Students:
  1. 24BCE0702 - Yash Pradhan
  2. 24BCE0714 - Anjini Pandey

Executes the full experimental matrix across:
- 4 Workload Types: High-Locality, Sequential, Uniform Random, Looping
- 3 Workload Sizes: N = 1000, 5000, 20000
- 3 Frame Capacities: 3, 5, 8
- 7 Algorithm Configurations: FIFO, LRU, Optimal, Clock, LFU, Adaptive (W=50), Adaptive (W=100)
- 5 Timing Repetitions per configuration for rigorous execution time statistics (mean, std, min, max)

Exports:
- results/raw_results.csv
- results/summary_results.csv
- results/belady_anomaly.csv
- report/experimental_setup.txt
"""

import os
import sys
import time
import math
import csv
import json
import platform
import statistics
from typing import List, Dict, Any

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.fifo import run_fifo
from src.lru import run_lru
from src.optimal import run_optimal
from src.clock import run_clock
from src.lfu import run_lfu
from src.adaptive import run_adaptive
from workload.workload_generator import get_all_workloads, SEED

REPETITIONS = 5
SIZES = [1000, 5000, 20000]
CAPACITIES = [3, 5, 8]
WORKLOAD_TYPES = ["high_locality", "sequential", "random", "looping"]

def record_hardware_and_environment(output_path: str):
    """
    Detects and records the genuine host environment without fabrication.
    """
    os_name = f"{platform.system()} {platform.release()} (Version: {platform.version()})"
    cpu_model = platform.processor() or platform.machine()
    python_ver = platform.python_version()

    # Determine RAM if possible
    ram_gb = "Unknown"
    try:
        import ctypes
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        ram_gb = f"{stat.ullTotalPhys / (1024**3):.2f} GB"
    except Exception:
        pass

    # Detect package versions
    pkg_versions = {}
    for pkg in ["matplotlib", "numpy"]:
        try:
            mod = __import__(pkg)
            pkg_versions[pkg] = getattr(mod, "__version__", "installed")
        except ImportError:
            pkg_versions[pkg] = "not installed"

    content = f"""======================================================================
OPERATING SYSTEMS (BCSE303L) EXPERIMENTAL ENVIRONMENT REPORT
Case Study: CS3 - Adaptive Page Replacement
Date/Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
======================================================================
1. HOST PLATFORM & SYSTEM SPECIFICATIONS
- Operating System : {os_name}
- CPU Architecture : {cpu_model} ({platform.machine()})
- Physical Memory  : {ram_gb}
- Python Version   : {python_ver} ({platform.python_implementation()})

2. INSTALLED LIBRARY VERSIONS
- matplotlib       : {pkg_versions.get('matplotlib')}
- numpy            : {pkg_versions.get('numpy')}

3. EXPERIMENTAL MATRIX CONFIGURATION
- Random Seed          : {SEED} (Deterministic)
- Workload Types (4)   : High-Locality, Sequential, Uniform Random, Looping
- Workload Sizes (3)   : N = 1,000, 5,000, 20,000 references
- Frame Capacities (3) : 3, 5, 8 frames
- Evaluated Algorithms : FIFO, LRU, Optimal, Clock, LFU, Adaptive (W=50, W=100)
- Timing Methodology   : time.perf_counter()
- Timing Repetitions   : {REPETITIONS} repetitions per condition
- Auxiliary Checks     : Belady's Anomaly empirical scan
======================================================================
"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Recorded experimental setup to {output_path}")

def run_belady_anomaly_experiment(output_path: str):
    """
    Evaluates Belady's Anomaly on FIFO using:
    1. Classic textbook anomaly string: [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5] across capacities 3 and 4
    2. Synthetic generated workloads across capacities 3, 4, 5, 6, 7, 8
    """
    rows = []

    # 1. Classic Anomaly Reference String
    classic_string = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    prev_faults = None
    for cap in [3, 4]:
        res = run_fifo(classic_string, cap, workload_type="classic_belady_string")
        anomaly_detected = (prev_faults is not None and res.page_faults > prev_faults)
        rows.append({
            "workload": "Classic Belady String (12 refs)",
            "frame_capacity": cap,
            "page_faults": res.page_faults,
            "page_hits": res.page_hits,
            "hit_ratio": round(res.hit_ratio, 4),
            "anomaly_demonstrated": "YES" if anomaly_detected else "NO",
            "notes": "Classic anomaly: capacity 4 yields 10 faults vs 9 faults on capacity 3" if anomaly_detected else "Baseline"
        })
        prev_faults = res.page_faults

    # 2. Check across synthetic workloads for N=1000 across capacities 3 through 8
    workloads = get_all_workloads(sizes=[1000], seed=SEED)
    for w_name, data in workloads.items():
        ref_str = data[1000]
        prev_f = None
        for cap in range(3, 9):
            res = run_fifo(ref_str, cap, workload_type=w_name)
            anomaly_detected = (prev_f is not None and res.page_faults > prev_f)
            rows.append({
                "workload": f"Synthetic {w_name} (N=1000)",
                "frame_capacity": cap,
                "page_faults": res.page_faults,
                "page_hits": res.page_hits,
                "hit_ratio": round(res.hit_ratio, 4),
                "anomaly_demonstrated": "YES" if anomaly_detected else "NO",
                "notes": "Monotonic decrease or stable" if not anomaly_detected else "Anomaly observed"
            })
            prev_f = res.page_faults

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["workload", "frame_capacity", "page_faults", "page_hits", "hit_ratio", "anomaly_demonstrated", "notes"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved Belady's Anomaly results to {output_path}")

def execute_experiment_matrix():
    print("=" * 70)
    print("LAUNCHING COMPREHENSIVE EXPERIMENT MATRIX")
    print(f"Sizes: {SIZES} | Capacities: {CAPACITIES} | Repetitions: {REPETITIONS}")
    print("=" * 70)

    workloads = get_all_workloads(sizes=SIZES, seed=SEED)

    raw_results: List[Dict[str, Any]] = []
    summary_results: List[Dict[str, Any]] = []

    # Map of algorithm execution runners
    algo_runners = {
        "FIFO": lambda r, c, wt: run_fifo(r, c, wt),
        "LRU": lambda r, c, wt: run_lru(r, c, wt),
        "Optimal": lambda r, c, wt: run_optimal(r, c, wt),
        "Clock": lambda r, c, wt: run_clock(r, c, wt),
        "LFU": lambda r, c, wt: run_lfu(r, c, wt),
        "Adaptive_W50": lambda r, c, wt: run_adaptive(r, c, window_size=50, workload_type=wt),
        "Adaptive_W100": lambda r, c, wt: run_adaptive(r, c, window_size=100, workload_type=wt),
    }

    total_configs = len(WORKLOAD_TYPES) * len(SIZES) * len(CAPACITIES) * len(algo_runners)
    config_idx = 0

    for w_type in WORKLOAD_TYPES:
        for n in SIZES:
            ref_str = workloads[w_type][n]
            for cap in CAPACITIES:
                for algo_name, runner in algo_runners.items():
                    config_idx += 1
                    timing_samples = []
                    runs_data = []

                    # Execute REPETITIONS
                    for rep in range(1, REPETITIONS + 1):
                        res = runner(ref_str, cap, w_type)
                        timing_samples.append(res.execution_time_sec)

                        raw_entry = {
                            "workload_type": w_type,
                            "N": n,
                            "frame_capacity": cap,
                            "algorithm": algo_name,
                            "repetition": rep,
                            "page_faults": res.page_faults,
                            "page_hits": res.page_hits,
                            "hit_ratio": round(res.hit_ratio, 6),
                            "execution_time_sec": res.execution_time_sec,
                            "switches_count": res.metadata.get("switches_count", 0),
                            "final_strategy": res.metadata.get("final_active_strategy", algo_name),
                            "random_seed": SEED
                        }
                        raw_results.append(raw_entry)
                        runs_data.append(res)

                    # Compute statistics across repetitions
                    mean_time = statistics.mean(timing_samples)
                    std_time = statistics.stdev(timing_samples) if len(timing_samples) > 1 else 0.0
                    min_time = min(timing_samples)
                    max_time = max(timing_samples)

                    base_res = runs_data[0]
                    summary_entry = {
                        "workload_type": w_type,
                        "N": n,
                        "frame_capacity": cap,
                        "algorithm": algo_name,
                        "page_faults": base_res.page_faults,
                        "page_hits": base_res.page_hits,
                        "hit_ratio": round(base_res.hit_ratio, 6),
                        "mean_execution_time_sec": round(mean_time, 8),
                        "std_execution_time_sec": round(std_time, 8),
                        "min_execution_time_sec": round(min_time, 8),
                        "max_execution_time_sec": round(max_time, 8),
                        "switches_count": base_res.metadata.get("switches_count", 0),
                        "final_strategy": base_res.metadata.get("final_active_strategy", algo_name),
                        "random_seed": SEED
                    }
                    summary_results.append(summary_entry)

                    if config_idx % 21 == 0 or config_idx == total_configs:
                        print(f"Progress: [{config_idx}/{total_configs}] {w_type} | N={n} | Cap={cap} | {algo_name} -> Faults: {base_res.page_faults} ({base_res.hit_ratio*100:.1f}%) | Time: {mean_time*1000:.3f}ms")

    # Save raw results
    raw_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "raw_results.csv"))
    with open(raw_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "workload_type", "N", "frame_capacity", "algorithm", "repetition",
            "page_faults", "page_hits", "hit_ratio", "execution_time_sec",
            "switches_count", "final_strategy", "random_seed"
        ])
        writer.writeheader()
        writer.writerows(raw_results)
    print(f"\nSaved {len(raw_results)} raw experimental rows to {raw_path}")

    # Save summary results
    summary_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "summary_results.csv"))
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "workload_type", "N", "frame_capacity", "algorithm",
            "page_faults", "page_hits", "hit_ratio",
            "mean_execution_time_sec", "std_execution_time_sec",
            "min_execution_time_sec", "max_execution_time_sec",
            "switches_count", "final_strategy", "random_seed"
        ])
        writer.writeheader()
        writer.writerows(summary_results)
    print(f"Saved {len(summary_results)} summary aggregated rows to {summary_path}")

    return raw_results, summary_results

if __name__ == "__main__":
    report_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "report", "experimental_setup.txt"))
    record_hardware_and_environment(report_env_path)

    belady_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "belady_anomaly.csv"))
    run_belady_anomaly_experiment(belady_path)

    execute_experiment_matrix()
