"""
Workload Generator for Page Replacement Simulation.
Course: BCSE303L - Operating Systems
Students:
  1. 24BCE0702 - Yash Pradhan
  2. 24BCE0714 - Anjini Pandey

Generates 4 distinct synthetic memory access patterns:
1. High-Locality: 80/20 Pareto principle access pattern (hot working set)
2. Sequential: Streaming sequential scans over a large page space
3. Uniform Random: Weak locality, uniformly distributed across page space
4. Looping: Cyclic loops over working sets (testing thrashing vs frame capacity)

Ensures reproducibility using fixed SEED = 42.
"""

import os
import random
import json
from typing import List, Dict

SEED = 42

def generate_high_locality_workload(n: int, total_pages: int = 50, hot_ratio: float = 0.2, hot_prob: float = 0.8, seed: int = SEED) -> List[int]:
    """
    Generates high-locality reference string using Pareto 80/20 distribution.
    hot_prob fraction of references come from the first (total_pages * hot_ratio) pages.
    """
    rng = random.Random(seed)
    num_hot = max(1, int(total_pages * hot_ratio))
    hot_pages = list(range(num_hot))
    cold_pages = list(range(num_hot, total_pages))

    refs = []
    for _ in range(n):
        if rng.random() < hot_prob:
            refs.append(rng.choice(hot_pages))
        else:
            refs.append(rng.choice(cold_pages))
    return refs

def generate_sequential_workload(n: int, total_pages: int = 50, scan_len: int = 25, seed: int = SEED) -> List[int]:
    """
    Generates sequential access pattern (streaming scans through page space).
    """
    rng = random.Random(seed)
    refs = []
    curr = 0
    for _ in range(n):
        refs.append(curr)
        curr = (curr + 1) % total_pages
        # Occasional random scan jump to simulate multiple sequential processes
        if rng.random() < 0.02:
            curr = rng.randint(0, total_pages - 1)
    return refs

def generate_random_workload(n: int, total_pages: int = 50, seed: int = SEED) -> List[int]:
    """
    Generates uniform random references with weak locality.
    """
    rng = random.Random(seed)
    return [rng.randint(0, total_pages - 1) for _ in range(n)]

def generate_looping_workload(n: int, loop_size: int = 6, seed: int = SEED) -> List[int]:
    """
    Generates repeated cyclic references over a working set of size 'loop_size'.
    Tests memory pressure and thrashing when loop_size > frame_capacity.
    """
    refs = []
    for i in range(n):
        refs.append(i % loop_size)
    return refs

def get_all_workloads(sizes: List[int] = [1000, 5000, 20000], seed: int = SEED) -> Dict[str, Dict[int, List[int]]]:
    """
    Generates and returns all workload types across all requested sizes.
    """
    workloads = {
        "high_locality": {},
        "sequential": {},
        "random": {},
        "looping": {}
    }
    for n in sizes:
        workloads["high_locality"][n] = generate_high_locality_workload(n, seed=seed)
        workloads["sequential"][n] = generate_sequential_workload(n, seed=seed)
        workloads["random"][n] = generate_random_workload(n, seed=seed)
        workloads["looping"][n] = generate_looping_workload(n, seed=seed)
    return workloads

def save_workload_traces(output_dir: str = None, sizes: List[int] = [1000, 5000, 20000], seed: int = SEED):
    """
    Saves generated workloads to JSON files for auditability and verification.
    """
    if output_dir is None:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "workload", "traces"))
    os.makedirs(output_dir, exist_ok=True)

    workloads = get_all_workloads(sizes=sizes, seed=seed)
    saved_files = []
    for w_type, size_dict in workloads.items():
        for n, trace in size_dict.items():
            filename = f"{w_type}_N{n}_seed{seed}.json"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({
                    "workload_type": w_type,
                    "N": n,
                    "seed": seed,
                    "references": trace
                }, f)
            saved_files.append(filepath)
    print(f"Generated and saved {len(saved_files)} workload traces to {output_dir}")
    return saved_files

if __name__ == "__main__":
    traces = save_workload_traces()
    print("Sample trace lengths:")
    for t in traces[:4]:
        print(" -", os.path.basename(t))
