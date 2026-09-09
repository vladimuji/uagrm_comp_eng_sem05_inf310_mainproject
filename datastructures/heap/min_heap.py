"""
Module: min_heap.py
Subject: INF310 - Data Structures II
Description: MinHeap, extends AbstractHeap so the smallest element is
             always at the root. Mirrors the Java MinHeap class.

Author: Vladimir
"""

from heap.abstract_heap import AbstractHeap


class MinHeap(AbstractHeap):
    """Heap where the smallest element has priority."""

    def has_priority(self, a, b):
        return a < b

    def get_min(self):
        return self.peek_root()