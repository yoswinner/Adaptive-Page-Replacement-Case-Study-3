"""
Optimal (Belady's MIN) Page Replacement Algorithm.
Course: BCSE303L - Operating Systems
Students:
  1. 24BCE0702 - Yash Pradhan
  2. 24BCE0714 - Anjini Pandey

Theoretical lookahead algorithm used solely as an optimal upper-bound baseline.
Note: Optimal utilizes future references; the adaptive algorithm never does.
"""

import time
from collections import defaultdict, deque
from typing import List, Set, Dict
from src.common import PageReplacementResult

def run_optimal(reference_string: List[int], frame_capacity: int, workload_type: str = "custom") -> PageReplacementResult:
    """
    Simulates Optimal (Belady's MIN) page replacement.
    Precomputes next occurrence indices for high efficiency O(N * capacity).
    Evicts the resident page that will not be used for the longest period of time.
    """
    if frame_capacity <= 0 or not reference_string:
        return PageReplacementResult(
            algorithm="Optimal",
            workload_type=workload_type,
            reference_count=len(reference_string),
            frame_capacity=frame_capacity,
            page_faults=0,
            page_hits=0,
            hit_ratio=0.0,
            execution_time_sec=0.0
        )

    start_time = time.perf_counter()

    # Precompute occurrence queues for O(1) next-use queries
    future_occurrences: Dict[int, deque] = defaultdict(deque)
    for idx, page in enumerate(reference_string):
        future_occurrences[page].append(idx)

    resident_set: List[int] = []  # Maintain stable resident list
    page_faults = 0
    page_hits = 0

    for current_idx, page in enumerate(reference_string):
        # Consume current occurrence from future queue
        future_occurrences[page].popleft()

        if page in resident_set:
            page_hits += 1
        else:
            page_faults += 1
            if len(resident_set) == frame_capacity:
                # Find page with farthest next occurrence
                farthest_idx = -1
                victim_page = None

                for resident_page in resident_set:
                    occ = future_occurrences[resident_page]
                    if not occ:
                        # Page is never used again in the future; immediate victim
                        victim_page = resident_page
                        break
                    else:
                        next_use = occ[0]
                        if next_use > farthest_idx:
                            farthest_idx = next_use
                            victim_page = resident_page

                resident_set.remove(victim_page)
            resident_set.append(page)

    elapsed_time = time.perf_counter() - start_time
    total_refs = len(reference_string)
    hit_ratio = page_hits / total_refs if total_refs > 0 else 0.0

    return PageReplacementResult(
        algorithm="Optimal",
        workload_type=workload_type,
        reference_count=total_refs,
        frame_capacity=frame_capacity,
        page_faults=page_faults,
        page_hits=page_hits,
        hit_ratio=hit_ratio,
        execution_time_sec=elapsed_time
    )
