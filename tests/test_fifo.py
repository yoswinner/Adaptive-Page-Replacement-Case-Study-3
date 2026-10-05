"""
Unit tests for FIFO page replacement.
"""

import unittest
from src.fifo import run_fifo

class TestFIFO(unittest.TestCase):
    def test_textbook_example(self):
        ref_str = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        res = run_fifo(ref_str, 3)
        self.assertEqual(res.page_faults, 15)
        self.assertEqual(res.page_hits, 5)
        self.assertAlmostEqual(res.hit_ratio, 0.25)

    def test_empty_reference_string(self):
        res = run_fifo([], 3)
        self.assertEqual(res.page_faults, 0)
        self.assertEqual(res.page_hits, 0)
        self.assertEqual(res.hit_ratio, 0.0)

    def test_single_frame(self):
        ref_str = [1, 2, 1, 3, 1, 4]
        res = run_fifo(ref_str, 1)
        # Every distinct change faults: 1 (F), 2 (F), 1 (F), 3 (F), 1 (F), 4 (F) -> 6 faults
        self.assertEqual(res.page_faults, 6)
        self.assertEqual(res.page_hits, 0)

    def test_repeated_same_page(self):
        ref_str = [5, 5, 5, 5, 5]
        res = run_fifo(ref_str, 2)
        self.assertEqual(res.page_faults, 1)
        self.assertEqual(res.page_hits, 4)

    def test_capacity_exceeds_unique_pages(self):
        ref_str = [1, 2, 3, 1, 2, 3, 1]
        res = run_fifo(ref_str, 5)
        self.assertEqual(res.page_faults, 3)
        self.assertEqual(res.page_hits, 4)

if __name__ == "__main__":
    unittest.main()
