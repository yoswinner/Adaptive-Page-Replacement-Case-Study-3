"""
Least Frequently Used (LFU) Page Replacement Algorithm.
Course: BCSE303L - Operating Systems
Students:
  1. 24BCE0702 - Yash Pradhan
  2. 24BCE0714 - Anjini Pandey

Semantics & Specification:
1. Frequency Tracking:
   - Tracks reference frequency for each currently loaded (resident) page.
   - Initial frequency upon arrival into a frame: 1.
   - Page Hit: increments resident page's frequency by 1.
2. Eviction Policy:
   - Evicts resident page with the minimum access frequency.
3. Deterministic Tie-Breaker:
   - FIFO (Oldest Arrival Order): When multiple resident pages have the identical
     minimum frequency, the page loaded earliest into memory (smallest arrival step)
     is selected as the eviction victim.
"""

import time
from typing import List, Dict
from src.common import PageReplacementResult

def run_lfu(reference_string: List[int], frame_capacity: int, workload_type: str = "custom") -> PageReplacementResult:
    if frame_capacity <= 0 or not reference_string:
        return PageReplacementResult(
            algorithm="LFU",
            workload_type=workload_type,
            reference_count=len(reference_string),
            frame_capacity=frame_capacity,
            page_faults=0,
            page_hits=0,
            hit_ratio=0.0,
            execution_time_sec=0.0
        )

    start_time = time.perf_counter()

    # resident map: page -> {"freq": int, "arrival_order": int}
    resident: Dict[int, Dict[str, int]] = {}
    page_faults = 0
    page_hits = 0

    for step, page in enumerate(reference_string):
        if page in resident:
            page_hits += 1
            resident[page]["freq"] += 1
        else:
            page_faults += 1
            if len(resident) == frame_capacity:
                # Find page with minimum frequency; tie-breaker: minimum arrival_order (FIFO)
                victim = min(
                    resident.keys(),
                    key=lambda p: (resident[p]["freq"], resident[p]["arrival_order"])
                )
                del resident[victim]

            resident[page] = {"freq": 1, "arrival_order": step}

    elapsed_time = time.perf_counter() - start_time
    total_refs = len(reference_string)
    hit_ratio = page_hits / total_refs if total_refs > 0 else 0.0

    return PageReplacementResult(
        algorithm="LFU",
        workload_type=workload_type,
        reference_count=total_refs,
        frame_capacity=frame_capacity,
        page_faults=page_faults,
        page_hits=page_hits,
        hit_ratio=hit_ratio,
        execution_time_sec=elapsed_time,
        metadata={"tie_breaker": "FIFO_arrival_order"}
    )
