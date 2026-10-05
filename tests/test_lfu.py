"""
Unit tests for LFU page replacement with FIFO tie-breaker.
"""

import unittest
from src.lfu import run_lfu

class TestLFU(unittest.TestCase):
    def test_textbook_example(self):
        ref_str = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        res = run_lfu(ref_str, 3)
        self.assertEqual(res.page_faults, 13)
        self.assertEqual(res.page_hits, 7)
        self.assertAlmostEqual(res.hit_ratio, 0.35)

    def test_empty_string(self):
        res = run_lfu([], 3)
        self.assertEqual(res.page_faults, 0)
        self.assertEqual(res.page_hits, 0)

    def test_frequency_based_eviction(self):
        # 1 accessed 3 times, 2 accessed 2 times, 3 accessed 1 time.
        # Capacity = 3. On page 4, 3 (freq=1) should be evicted.
        ref_str = [1, 1, 1, 2, 2, 3, 4]
        res = run_lfu(ref_str, 3)
        # 1(F), 1(H), 1(H), 2(F), 2(H), 3(F), 4(F, evicts 3) -> 4 faults, 3 hits
        self.assertEqual(res.page_faults, 4)
        self.assertEqual(res.page_hits, 3)

    def test_fifo_tie_breaking(self):
        # 1, 2, 3 all have freq=1. Next is 4. Page 1 arrived earliest, so 1 should be evicted.
        # Then 1 comes back: should fault.
        ref_str = [1, 2, 3, 4, 1]
        res = run_lfu(ref_str, 3)
        # 1(F), 2(F), 3(F), 4(F evicts 1), 1(F evicts 2) -> 5 faults
        self.assertEqual(res.page_faults, 5)
        self.assertEqual(res.page_hits, 0)

if __name__ == "__main__":
    unittest.main()
