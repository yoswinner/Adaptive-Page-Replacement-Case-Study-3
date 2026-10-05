"""
Least Recently Used (LRU) Page Replacement Algorithm.
Course: BCSE303L - Operating Systems
Students:
  1. 24BCE0702 - Yash Pradhan
  2. 24BCE0714 - Anjini Pandey
"""

import time
from collections import OrderedDict
from typing import List
from src.common import PageReplacementResult

def run_lru(reference_string: List[int], frame_capacity: int, workload_type: str = "custom") -> PageReplacementResult:
    """
    Simulates LRU page replacement.
    Maintains an OrderedDict where the front is the least recently used
    and the end is the most recently used.
    """
    if frame_capacity <= 0 or not reference_string:
        return PageReplacementResult(
            algorithm="LRU",
            workload_type=workload_type,
            reference_count=len(reference_string),
            frame_capacity=frame_capacity,
            page_faults=0,
            page_hits=0,
            hit_ratio=0.0,
            execution_time_sec=0.0
        )

    start_time = time.perf_counter()

    resident_frames = OrderedDict()  # page -> dummy/timestamp
    page_faults = 0
    page_hits = 0

    for page in reference_string:
        if page in resident_frames:
            page_hits += 1
            resident_frames.move_to_end(page)
        else:
            page_faults += 1
            if len(resident_frames) == frame_capacity:
                resident_frames.popitem(last=False)  # evicts least recently used
            resident_frames[page] = True

    elapsed_time = time.perf_counter() - start_time
    total_refs = len(reference_string)
    hit_ratio = page_hits / total_refs if total_refs > 0 else 0.0

    return PageReplacementResult(
        algorithm="LRU",
        workload_type=workload_type,
        reference_count=total_refs,
        frame_capacity=frame_capacity,
        page_faults=page_faults,
        page_hits=page_hits,
        hit_ratio=hit_ratio,
        execution_time_sec=elapsed_time
    )
