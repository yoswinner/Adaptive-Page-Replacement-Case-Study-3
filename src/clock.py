"""
Clock (Second-Chance) Page Replacement Algorithm.
Course: BCSE303L - Operating Systems
Students:
  1. 24BCE0702 - Yash Pradhan
  2. 24BCE0714 - Anjini Pandey

Semantics & Specification:
1. Frame structure: Circular buffer of fixed size 'frame_capacity'.
   Each frame holds: {'page': int, 'ref_bit': int (0 or 1)}.
2. Initial pointer position: hand = 0.
3. Page Hit:
   - If accessed page is resident, set its ref_bit = 1.
   - Hand pointer position DOES NOT advance on a hit.
4. Page Fault with empty frames:
   - Insert page with ref_bit = 1 into next available slot.
   - Hand pointer advances to (hand + 1) % frame_capacity.
5. Page Fault when frames are full (Eviction):
   - Circularly scan starting from 'hand':
     * If ref_bit == 1: clear bit (ref_bit = 0), advance hand = (hand + 1) % frame_capacity.
     * If ref_bit == 0: victim found. Evict this page, replace with incoming page,
       set ref_bit = 1, advance hand = (hand + 1) % frame_capacity, and terminate scan.
"""

import time
from typing import List, Optional, Dict
from src.common import PageReplacementResult

def run_clock(reference_string: List[int], frame_capacity: int, workload_type: str = "custom") -> PageReplacementResult:
    if frame_capacity <= 0 or not reference_string:
        return PageReplacementResult(
            algorithm="Clock",
            workload_type=workload_type,
            reference_count=len(reference_string),
            frame_capacity=frame_capacity,
            page_faults=0,
            page_hits=0,
            hit_ratio=0.0,
            execution_time_sec=0.0
        )

    start_time = time.perf_counter()

    # Circular buffer of frames: list of dicts [{'page': int, 'ref_bit': int}]
    frames: List[Dict[str, int]] = []
    hand = 0
    page_faults = 0
    page_hits = 0

    for page in reference_string:
        # Check if page is already resident
        hit_idx = -1
        for idx, f in enumerate(frames):
            if f["page"] == page:
                hit_idx = idx
                break

        if hit_idx != -1:
            page_hits += 1
            frames[hit_idx]["ref_bit"] = 1
        else:
            page_faults += 1
            if len(frames) < frame_capacity:
                frames.append({"page": page, "ref_bit": 1})
                hand = (hand + 1) % frame_capacity
            else:
                while True:
                    if frames[hand]["ref_bit"] == 0:
                        # Evict victim and place new page
                        frames[hand] = {"page": page, "ref_bit": 1}
                        hand = (hand + 1) % frame_capacity
                        break
                    else:
                        # Give second chance: clear bit and advance hand
                        frames[hand]["ref_bit"] = 0
                        hand = (hand + 1) % frame_capacity

    elapsed_time = time.perf_counter() - start_time
    total_refs = len(reference_string)
    hit_ratio = page_hits / total_refs if total_refs > 0 else 0.0

    return PageReplacementResult(
        algorithm="Clock",
        workload_type=workload_type,
        reference_count=total_refs,
        frame_capacity=frame_capacity,
        page_faults=page_faults,
        page_hits=page_hits,
        hit_ratio=hit_ratio,
        execution_time_sec=elapsed_time,
        metadata={"clock_hand_final": hand}
    )
