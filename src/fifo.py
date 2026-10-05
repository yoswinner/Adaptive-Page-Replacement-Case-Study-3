"""
First-In, First-Out (FIFO) Page Replacement Algorithm.
Course: BCSE303L - Operating Systems
Students:
  1. 24BCE0702 - Yash Pradhan
  2. 24BCE0714 - Anjini Pandey
"""

import time
from collections import deque
from typing import List, Set
from src.common import PageReplacementResult

def run_fifo(reference_string: List[int], frame_capacity: int, workload_type: str = "custom") -> PageReplacementResult:
    """
    Simulates FIFO page replacement.
    Maintains a strict queue-based replacement order.
    """
    if frame_capacity <= 0 or not reference_string:
        return PageReplacementResult(
            algorithm="FIFO",
            workload_type=workload_type,
            reference_count=len(reference_string),
            frame_capacity=frame_capacity,
            page_faults=0,
            page_hits=0,
            hit_ratio=0.0,
            execution_time_sec=0.0
        )

    start_time = time.perf_counter()

    queue = deque()
    resident_set: Set[int] = set()
    page_faults = 0
    page_hits = 0

    for page in reference_string:
        if page in resident_set:
            page_hits += 1
        else:
            page_faults += 1
            if len(queue) == frame_capacity:
                evicted_page = queue.popleft()
                resident_set.remove(evicted_page)
            queue.append(page)
            resident_set.add(page)

    elapsed_time = time.perf_counter() - start_time
    total_refs = len(reference_string)
    hit_ratio = page_hits / total_refs if total_refs > 0 else 0.0

    return PageReplacementResult(
        algorithm="FIFO",
        workload_type=workload_type,
        reference_count=total_refs,
        frame_capacity=frame_capacity,
        page_faults=page_faults,
        page_hits=page_hits,
        hit_ratio=hit_ratio,
        execution_time_sec=elapsed_time
    )
