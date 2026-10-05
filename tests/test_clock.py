"""
Unit tests for Clock (Second-Chance) page replacement.
"""

import unittest
from src.clock import run_clock

class TestClock(unittest.TestCase):
    def test_textbook_example(self):
        ref_str = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        res = run_clock(ref_str, 3)
        self.assertEqual(res.page_faults, 14)
        self.assertEqual(res.page_hits, 6)
        self.assertAlmostEqual(res.hit_ratio, 0.30)

    def test_empty_string(self):
        res = run_clock([], 3)
        self.assertEqual(res.page_faults, 0)
        self.assertEqual(res.page_hits, 0)

    def test_single_frame(self):
        ref_str = [1, 2, 1, 3]
        res = run_clock(ref_str, 1)
        self.assertEqual(res.page_faults, 4)
        self.assertEqual(res.page_hits, 0)

    def test_repeated_pages(self):
        ref_str = [1, 1, 1, 2, 2, 3, 3]
        res = run_clock(ref_str, 2)
        # 1(F), 1(H), 1(H), 2(F), 2(H), 3(F: 1 and 2 both had ref_bit=1, sweep clears, evicts 1) -> 3 faults, 4 hits
        self.assertEqual(res.page_faults, 3)
        self.assertEqual(res.page_hits, 4)

if __name__ == "__main__":
    unittest.main()
