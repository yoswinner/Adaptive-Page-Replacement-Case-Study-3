"""
Adaptive Page Replacement Policy.
Course: BCSE303L - Operating Systems
Students:
  1. 24BCE0702 - Yash Pradhan
  2. 24BCE0714 - Anjini Pandey

Online, causal, and locality-driven page replacement mechanism.
- Strictly CAUSAL: Uses only past references within a rolling window W.
- NEVER accesses future references, future faults, or hindsight oracle comparisons.
- Evaluates observable locality metrics:
  * Unique Page Ratio U = unique_pages / window_size
  * Frequency Skew (Coefficient of Variation) = std_freq / mean_freq
- Deterministically switches between LRU, LFU and Clock (FIFO handover state is
  implemented but FIFO is never chosen by the current decision rules).
- Preserves physical resident frames across strategy switches (no cold memory wipes).
"""

import time
import math
from collections import deque, Counter, OrderedDict
from typing import List, Dict, Any, Optional
from src.common import PageReplacementResult

class AdaptiveEngine:
    """
    Maintains memory state and applies dynamic policy adaptation based
    on observed rolling-window locality metrics.
    """
    def __init__(
        self,
        frame_capacity: int,
        window_size: int = 50,
        locality_threshold_U: float = 0.35,
        scan_threshold_U: float = 0.85,
        frequency_skew_threshold: float = 1.0,
        initial_strategy: str = "LRU"
    ):
        self.capacity = frame_capacity
        self.window_size = window_size
        self.locality_threshold_U = locality_threshold_U
        self.scan_threshold_U = scan_threshold_U
        self.frequency_skew_threshold = frequency_skew_threshold
        self.active_strategy = initial_strategy

        # Resident physical pages (set of currently loaded pages)
        self.resident_set = set()

        # Policy-specific auxiliary metadata
        # LRU state: OrderedDict (front = LRU, back = MRU)
        self.lru_order = OrderedDict()

        # LFU state: page -> {"freq": int, "arrival": int}
        self.lfu_state: Dict[int, Dict[str, int]] = {}

        # Clock state: list of {"page": int, "ref_bit": int}, hand index
        self.clock_frames: List[Dict[str, int]] = []
        self.clock_hand: int = 0

        # FIFO state: deque of page IDs
        self.fifo_queue = deque()

        # Observation window (rolling history of recent page references)
        self.history_window = deque(maxlen=window_size)

        # Telemetry
        self.page_faults = 0
        self.page_hits = 0
        self.switches_count = 0
        self.strategy_steps = {"LRU": 0, "LFU": 0, "Clock": 0, "FIFO": 0}
        self.decision_log = []

    def _sync_state_on_switch(self, old_strat: str, new_strat: str, current_step: int):
        """
        Preserves resident physical frames and reconstructs auxiliary state
        for the newly active strategy without wiping physical memory.
        """
        if old_strat == new_strat:
            return

        self.switches_count += 1

        # Reconstruct state for new strategy using window history and current resident set
        if new_strat == "LRU":
            # Order resident pages by their most recent appearance in the history window
            # Pages not in window placed at the front (oldest)
            new_order = OrderedDict()
            window_list = list(self.history_window)
            last_seen = {}
            for idx, p in enumerate(window_list):
                if p in self.resident_set:
                    last_seen[p] = idx

            # Add pages not in window first (least recently used)
            for p in self.resident_set:
                if p not in last_seen:
                    new_order[p] = True

            # Add pages in window sorted by their last access index
            for p, _ in sorted(last_seen.items(), key=lambda item: item[1]):
                new_order[p] = True

            self.lru_order = new_order

        elif new_strat == "LFU":
            # Reconstruct frequencies from window counts; minimum frequency 1
            counts = Counter(self.history_window)
            self.lfu_state = {}
            for p in self.resident_set:
                freq = max(1, counts.get(p, 1))
                self.lfu_state[p] = {"freq": freq, "arrival": current_step}

        elif new_strat == "Clock":
            # Reconstruct circular buffer from resident set, ref_bit = 1
            self.clock_frames = [{"page": p, "ref_bit": 1} for p in self.resident_set]
            self.clock_hand = 0

        elif new_strat == "FIFO":
            # Maintain resident pages in deterministic order
            self.fifo_queue = deque(list(self.resident_set))

    def _evaluate_locality_and_select_policy(self) -> str:
        """
        Computes rolling-window locality metrics over past references
        and selects the appropriate replacement policy deterministically.
        """
        if len(self.history_window) < min(10, self.window_size):
            return self.active_strategy

        w_len = len(self.history_window)
        unique_pages = len(set(self.history_window))
        u_ratio = unique_pages / w_len

        # Calculate frequency skew (Coefficient of Variation: std / mean)
        counts = Counter(self.history_window)
        freqs = list(counts.values())
        mean_f = sum(freqs) / len(freqs)
        variance_f = sum((f - mean_f) ** 2 for f in freqs) / len(freqs)
        std_f = math.sqrt(variance_f)
        cv_f = (std_f / mean_f) if mean_f > 0 else 0.0

        # Decision rules
        if u_ratio < self.locality_threshold_U:
            # Strong temporal locality: LRU protects working set best
            selected = "LRU"
        elif u_ratio >= self.scan_threshold_U:
            # Scanning / high diversity: Clock handles scans without polluting LRU cache
            selected = "Clock"
        elif cv_f >= self.frequency_skew_threshold and u_ratio < 0.70:
            # High frequency skew with moderate diversity: LFU protects frequent pages
            selected = "LFU"
        else:
            # Moderate locality: default to LRU
            selected = "LRU"

        return selected

    def reference(self, page: int, step: int):
        """
        Processes a single memory reference in an online, causal manner.
        """
        # Periodic adaptation check: only when the window is full AND every max(10, W // 2) steps.
        # Uses only past references (the current page is appended to the window afterwards).
        if len(self.history_window) == self.window_size and step % max(10, self.window_size // 2) == 0:
            new_strat = self._evaluate_locality_and_select_policy()
            if new_strat != self.active_strategy:
                self._sync_state_on_switch(self.active_strategy, new_strat, step)
                self.active_strategy = new_strat

        self.strategy_steps[self.active_strategy] = self.strategy_steps.get(self.active_strategy, 0) + 1

        is_hit = page in self.resident_set

        if is_hit:
            self.page_hits += 1
            # Update active strategy state
            if self.active_strategy == "LRU":
                self.lru_order.move_to_end(page)
            elif self.active_strategy == "LFU":
                self.lfu_state[page]["freq"] += 1
            elif self.active_strategy == "Clock":
                for f in self.clock_frames:
                    if f["page"] == page:
                        f["ref_bit"] = 1
                        break
            elif self.active_strategy == "FIFO":
                pass
        else:
            self.page_faults += 1
            if len(self.resident_set) < self.capacity:
                # Add to resident set and active strategy state
                self.resident_set.add(page)
                if self.active_strategy == "LRU":
                    self.lru_order[page] = True
                elif self.active_strategy == "LFU":
                    self.lfu_state[page] = {"freq": 1, "arrival": step}
                elif self.active_strategy == "Clock":
                    self.clock_frames.append({"page": page, "ref_bit": 1})
                    self.clock_hand = (self.clock_hand + 1) % self.capacity
                elif self.active_strategy == "FIFO":
                    self.fifo_queue.append(page)
            else:
                # Eviction required using active strategy
                victim = None
                if self.active_strategy == "LRU":
                    victim, _ = self.lru_order.popitem(last=False)
                    self.lru_order[page] = True
                elif self.active_strategy == "LFU":
                    victim = min(
                        self.lfu_state.keys(),
                        key=lambda p: (self.lfu_state[p]["freq"], self.lfu_state[p]["arrival"])
                    )
                    del self.lfu_state[victim]
                    self.lfu_state[page] = {"freq": 1, "arrival": step}
                elif self.active_strategy == "Clock":
                    while True:
                        if self.clock_frames[self.clock_hand]["ref_bit"] == 0:
                            victim = self.clock_frames[self.clock_hand]["page"]
                            self.clock_frames[self.clock_hand] = {"page": page, "ref_bit": 1}
                            self.clock_hand = (self.clock_hand + 1) % self.capacity
                            break
                        else:
                            self.clock_frames[self.clock_hand]["ref_bit"] = 0
                            self.clock_hand = (self.clock_hand + 1) % self.capacity
                elif self.active_strategy == "FIFO":
                    victim = self.fifo_queue.popleft()
                    self.fifo_queue.append(page)

                if victim is not None and victim in self.resident_set:
                    self.resident_set.remove(victim)
                self.resident_set.add(page)

        # Update sliding history window
        self.history_window.append(page)

def run_adaptive(
    reference_string: List[int],
    frame_capacity: int,
    window_size: int = 50,
    locality_threshold_U: float = 0.35,
    scan_threshold_U: float = 0.85,
    frequency_skew_threshold: float = 1.0,
    initial_strategy: str = "LRU",
    workload_type: str = "custom"
) -> PageReplacementResult:
    """
    Executes Adaptive page replacement over the reference string.
    Measures execution time with time.perf_counter().
    """
    if frame_capacity <= 0 or not reference_string:
        return PageReplacementResult(
            algorithm="Adaptive",
            workload_type=workload_type,
            reference_count=len(reference_string),
            frame_capacity=frame_capacity,
            page_faults=0,
            page_hits=0,
            hit_ratio=0.0,
            execution_time_sec=0.0,
            metadata={
                "adaptive_window": window_size,
                "switches_count": 0,
                "strategy_steps": {"LRU": 0, "LFU": 0, "Clock": 0, "FIFO": 0}
            }
        )

    start_time = time.perf_counter()

    engine = AdaptiveEngine(
        frame_capacity=frame_capacity,
        window_size=window_size,
        locality_threshold_U=locality_threshold_U,
        scan_threshold_U=scan_threshold_U,
        frequency_skew_threshold=frequency_skew_threshold,
        initial_strategy=initial_strategy
    )

    for step, page in enumerate(reference_string):
        engine.reference(page, step)

    elapsed_time = time.perf_counter() - start_time
    total_refs = len(reference_string)
    hit_ratio = engine.page_hits / total_refs if total_refs > 0 else 0.0

    return PageReplacementResult(
        algorithm="Adaptive",
        workload_type=workload_type,
        reference_count=total_refs,
        frame_capacity=frame_capacity,
        page_faults=engine.page_faults,
        page_hits=engine.page_hits,
        hit_ratio=hit_ratio,
        execution_time_sec=elapsed_time,
        metadata={
            "adaptive_window": window_size,
            "switches_count": engine.switches_count,
            "strategy_steps": engine.strategy_steps,
            "final_active_strategy": engine.active_strategy
        }
    )
