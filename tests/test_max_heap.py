"""Tests for the hand-written MaxHeap class (no heapq dependency).

Exercises push, pop, peek, sift_up, sift_down, tie-breaking, and
edge cases (empty heap, single element, large random sequences).
"""

import unittest
import random

from data_structures.heap import MaxHeap


def make_entry(score, counter, sid="s"):
    """Build a heap entry tuple (score, counter, song_id, song)."""
    return (score, counter, sid, {"song_id": sid, "score": score})


class TestMaxHeapBasic(unittest.TestCase):
    """Basic push / pop / peek behaviour."""

    def test_empty_heap_len(self):
        h = MaxHeap()
        self.assertEqual(len(h), 0)
        self.assertFalse(h)

    def test_push_increments_len(self):
        h = MaxHeap()
        h.push(make_entry(1.0, 0))
        self.assertEqual(len(h), 1)
        h.push(make_entry(2.0, 1))
        self.assertEqual(len(h), 2)

    def test_pop_empty_raises(self):
        h = MaxHeap()
        with self.assertRaises(IndexError):
            h.pop()

    def test_peek_empty_raises(self):
        h = MaxHeap()
        with self.assertRaises(IndexError):
            h.peek()

    def test_peek_does_not_remove(self):
        h = MaxHeap()
        h.push(make_entry(5.0, 0, "a"))
        entry = h.peek()
        self.assertEqual(entry[0], 5.0)
        self.assertEqual(len(h), 1)

    def test_push_one_pop_one(self):
        h = MaxHeap()
        h.push(make_entry(3.0, 0, "a"))
        entry = h.pop()
        self.assertEqual(entry[2], "a")
        self.assertEqual(len(h), 0)


class TestMaxHeapOrdering(unittest.TestCase):
    """Verify that pop always returns the highest-priority element."""

    def test_pop_returns_max(self):
        h = MaxHeap()
        h.push(make_entry(1.0, 0, "a"))
        h.push(make_entry(5.0, 1, "b"))
        h.push(make_entry(3.0, 2, "c"))
        top = h.pop()
        self.assertEqual(top[0], 5.0)
        self.assertEqual(top[2], "b")

    def test_pop_all_descending(self):
        h = MaxHeap()
        scores = [7, 2, 9, 1, 5, 3, 8, 4, 6, 0]
        for i, s in enumerate(scores):
            h.push(make_entry(float(s), i, f"s{i}"))
        popped = [h.pop()[0] for _ in range(len(scores))]
        self.assertEqual(popped, sorted(scores, reverse=True))

    def test_ascending_insert_descending_pop(self):
        """Insert 0..99 ascending, pop must return 99..0."""
        h = MaxHeap()
        for i in range(100):
            h.push(make_entry(float(i), i, f"s{i}"))
        for i in range(99, -1, -1):
            self.assertEqual(h.pop()[0], float(i))

    def test_descending_insert_descending_pop(self):
        """Insert 99..0 descending, pop must still return 99..0."""
        h = MaxHeap()
        for i in range(99, -1, -1):
            h.push(make_entry(float(i), 99 - i, f"s{i}"))
        for i in range(99, -1, -1):
            self.assertEqual(h.pop()[0], float(i))


class TestMaxHeapTieBreak(unittest.TestCase):
    """When scores are equal, lower counter (earlier insert) wins."""

    def test_tie_break_fifo(self):
        h = MaxHeap()
        h.push(make_entry(5.0, 0, "first"))
        h.push(make_entry(5.0, 1, "second"))
        h.push(make_entry(5.0, 2, "third"))
        self.assertEqual(h.pop()[2], "first")
        self.assertEqual(h.pop()[2], "second")
        self.assertEqual(h.pop()[2], "third")

    def test_tie_break_interleaved(self):
        h = MaxHeap()
        h.push(make_entry(1.0, 0, "low0"))
        h.push(make_entry(9.0, 1, "hi1"))
        h.push(make_entry(9.0, 2, "hi2"))
        h.push(make_entry(1.0, 3, "low3"))
        # Two 9.0s: counter 1 before 2
        self.assertEqual(h.pop()[2], "hi1")
        self.assertEqual(h.pop()[2], "hi2")
        # Two 1.0s: counter 0 before 3
        self.assertEqual(h.pop()[2], "low0")
        self.assertEqual(h.pop()[2], "low3")


class TestMaxHeapLarge(unittest.TestCase):
    """Stress test with random data against a reference sort."""

    def test_random_1000(self):
        rng = random.Random(12345)
        values = [rng.randint(0, 100000) for _ in range(1000)]
        h = MaxHeap()
        for i, v in enumerate(values):
            h.push(make_entry(float(v), i, f"s{i}"))
        popped = [h.pop()[0] for _ in range(1000)]
        self.assertEqual(popped, sorted(values, reverse=True))

    def test_duplicate_scores(self):
        """All same score -- pop order must follow counter (FIFO)."""
        h = MaxHeap()
        n = 500
        for i in range(n):
            h.push(make_entry(42.0, i, f"s{i}"))
        for i in range(n):
            self.assertEqual(h.pop()[2], f"s{i}")

    def test_push_pop_interleaved(self):
        """Mix of pushes and pops should always keep heap property."""
        rng = random.Random(99)
        h = MaxHeap()
        reference = []  # sorted descending reference
        for _ in range(200):
            v = rng.randint(0, 1000)
            h.push(make_entry(float(v), len(reference), f"s{v}_{len(reference)}"))
            reference.append(v)
            if len(h) > 3 and rng.random() < 0.5:
                top = h.pop()
                expected = max(reference)
                self.assertEqual(top[0], float(expected))
                reference.remove(expected)


class TestMaxHeapClear(unittest.TestCase):

    def test_clear_empties(self):
        h = MaxHeap()
        for i in range(10):
            h.push(make_entry(float(i), i))
        self.assertEqual(len(h), 10)
        h.clear()
        self.assertEqual(len(h), 0)
        self.assertFalse(h)

    def test_clear_then_push(self):
        h = MaxHeap()
        h.push(make_entry(1.0, 0))
        h.clear()
        h.push(make_entry(5.0, 1, "after"))
        self.assertEqual(len(h), 1)
        self.assertEqual(h.pop()[2], "after")


class TestMaxHeapIndexHelpers(unittest.TestCase):
    """Verify the parent / child index math directly."""

    def test_parent_of_root(self):
        # Root has no real parent; (0-1)//2 == -1 in Python.
        # sift_up guards with `while i > 0` so this is never used.
        self.assertEqual(MaxHeap._parent(0), -1)

    def test_parent_child_relationship(self):
        for i in range(1, 100):
            left = MaxHeap._left(i)
            right = MaxHeap._right(i)
            self.assertEqual(MaxHeap._parent(left), i)
            self.assertEqual(MaxHeap._parent(right), i)


if __name__ == "__main__":
    unittest.main()
