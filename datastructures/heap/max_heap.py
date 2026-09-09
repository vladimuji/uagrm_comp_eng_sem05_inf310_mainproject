"""
Module: max_heap.py
Subject: INF310 - Data Structures II
Description: MaxHeap, extends AbstractHeap so the largest element is
             always at the root. Mirrors the Java MaxHeap class.

Author: Vladimir
"""

from heap.abstract_heap import AbstractHeap


class MaxHeap(AbstractHeap):
    """Heap where the largest element has priority."""

    def has_priority(self, a, b):
        return a > b

    def get_max(self):
        return self.peek_root()