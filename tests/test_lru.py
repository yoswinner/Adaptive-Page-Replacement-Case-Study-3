"""
Unit tests for LRU page replacement.
"""

import unittest
from src.lru import run_lru

class TestLRU(unittest.TestCase):
    def test_textbook_example(self):
        ref_str = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        res = run_lru(ref_str, 3)
        self.assertEqual(res.page_faults, 12)
        self.assertEqual(res.page_hits, 8)
        self.assertAlmostEqual(res.hit_ratio, 0.40)

    def test_empty_string(self):
        res = run_lru([], 3)
        self.assertEqual(res.page_faults, 0)
        self.assertEqual(res.page_hits, 0)

    def test_all_unique_pages(self):
        ref_str = [1, 2, 3, 4, 5]
        res = run_lru(ref_str, 3)
        self.assertEqual(res.page_faults, 5)
        self.assertEqual(res.page_hits, 0)

    def test_looping_workload(self):
        # working set = 4, frames = 3: strict LRU should fault on every access in loop
        ref_str = [1, 2, 3, 4, 1, 2, 3, 4]
        res = run_lru(ref_str, 3)
        self.assertEqual(res.page_faults, 8)
        self.assertEqual(res.page_hits, 0)

if __name__ == "__main__":
    unittest.main()
