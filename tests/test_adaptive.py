"""
Unit tests for the Adaptive Page Replacement policy.
Course: BCSE303L - Operating Systems
Students:
  1. 24BCE0702 - Yash Pradhan
  2. 24BCE0714 - Anjini Pandey
"""

import unittest
from src.adaptive import run_adaptive
from workload.workload_generator import (
    generate_high_locality_workload,
    generate_sequential_workload,
    generate_looping_workload,
    generate_random_workload
)

class TestAdaptive(unittest.TestCase):
    def test_invariants_and_accounting(self):
        """Verify page_faults + page_hits == N and hit_ratio == hits / N"""
        ref_str = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        res = run_adaptive(ref_str, frame_capacity=3, window_size=50)
        self.assertEqual(res.page_faults + res.page_hits, len(ref_str))
        self.assertAlmostEqual(res.hit_ratio, res.page_hits / len(ref_str))

    def test_empty_reference_string(self):
        res = run_adaptive([], frame_capacity=3, window_size=50)
        self.assertEqual(res.page_faults, 0)
        self.assertEqual(res.page_hits, 0)
        self.assertEqual(res.hit_ratio, 0.0)

    def test_single_frame(self):
        ref_str = [1, 2, 1, 3, 1, 4]
        res = run_adaptive(ref_str, frame_capacity=1, window_size=50)
        self.assertEqual(res.page_faults + res.page_hits, len(ref_str))
        self.assertEqual(res.page_faults, 6)

    def test_repeated_page(self):
        ref_str = [5] * 20
        res = run_adaptive(ref_str, frame_capacity=3, window_size=50)
        self.assertEqual(res.page_faults, 1)
        self.assertEqual(res.page_hits, 19)

    def test_window_sizes(self):
        """Test with W=50 and W=100"""
        workload = generate_high_locality_workload(500, seed=42)
        res_w50 = run_adaptive(workload, frame_capacity=5, window_size=50)
        res_w100 = run_adaptive(workload, frame_capacity=5, window_size=100)
        self.assertEqual(res_w50.page_faults + res_w50.page_hits, 500)
        self.assertEqual(res_w100.page_faults + res_w100.page_hits, 500)

    def test_sequential_switches_to_clock(self):
        """A purely sequential scan (high unique page ratio) should trigger Clock/FIFO policy"""
        scan_workload = list(range(200))  # 200 all-unique consecutive pages
        res = run_adaptive(scan_workload, frame_capacity=4, window_size=50, scan_threshold_U=0.8)
        self.assertEqual(res.metadata["final_active_strategy"], "Clock")

    def test_high_locality_stays_lru(self):
        """A tight working set should keep LRU active"""
        tight_workload = [1, 2, 3] * 50  # 3 unique pages in 150 accesses (U = 3/50 = 0.06)
        res = run_adaptive(tight_workload, frame_capacity=4, window_size=50, locality_threshold_U=0.35)
        self.assertEqual(res.metadata["final_active_strategy"], "LRU")

    def test_deterministic_behavior(self):
        """Same workload must yield exact identical faults and hits across runs"""
        workload = generate_random_workload(300, seed=42)
        res1 = run_adaptive(workload, frame_capacity=5, window_size=50)
        res2 = run_adaptive(workload, frame_capacity=5, window_size=50)
        self.assertEqual(res1.page_faults, res2.page_faults)
        self.assertEqual(res1.page_hits, res2.page_hits)

    def test_causality_future_independence(self):
        """Changing references AFTER step k must not change any decision or fault up to step k."""
        from src.adaptive import AdaptiveEngine

        def trace(ref):
            eng = AdaptiveEngine(frame_capacity=5, window_size=50)
            log = []
            for i, p in enumerate(ref):
                eng.reference(p, i)
                log.append((eng.page_faults, eng.active_strategy, frozenset(eng.resident_set)))
            return log

        base = generate_sequential_workload(1000, seed=42)
        full = trace(base)
        for k in (100, 437, 900):
            altered = base[:k] + [500 + (i % 7) for i in range(len(base) - k)]
            self.assertEqual(trace(altered)[:k], full[:k])

if __name__ == "__main__":
    unittest.main()
