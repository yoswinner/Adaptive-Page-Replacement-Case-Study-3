"""
Unit tests for Optimal (Belady's MIN) page replacement.
"""

import unittest
from src.optimal import run_optimal
from src.fifo import run_fifo
from src.lru import run_lru

class TestOptimal(unittest.TestCase):
    def test_textbook_example(self):
        ref_str = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        res = run_optimal(ref_str, 3)
        self.assertEqual(res.page_faults, 9)
        self.assertEqual(res.page_hits, 11)
        self.assertAlmostEqual(res.hit_ratio, 0.55)

    def test_optimal_is_lower_bound_on_faults(self):
        ref_str = [1, 2, 3, 4, 2, 1, 5, 6, 2, 1, 2, 3, 7, 6, 3, 2, 1, 2, 3, 6]
        res_opt = run_optimal(ref_str, 3)
        res_fifo = run_fifo(ref_str, 3)
        res_lru = run_lru(ref_str, 3)
        self.assertLessEqual(res_opt.page_faults, res_fifo.page_faults)
        self.assertLessEqual(res_opt.page_faults, res_lru.page_faults)

    def test_empty_string(self):
        res = run_optimal([], 3)
        self.assertEqual(res.page_faults, 0)
        self.assertEqual(res.page_hits, 0)

if __name__ == "__main__":
    unittest.main()
