"""
Module: abstract_heap.py
Subject: INF310 - Data Structures II
Description: AbstractHeap, implements the array-based heap mechanics
             (insert, extract_root, peek_root, heapify up/down,
             build_heap) shared by MinHeap and MaxHeap, leaving only
             has_priority as abstract. Mirrors the Java AbstractHeap
             class.

Author: Vladimir
"""

from abc import abstractmethod

from heap.i_heap import IHeap


class AbstractHeap(IHeap):
    """Array-based heap: implements everything except has_priority."""

    def __init__(self):
        self._heap_array = []

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def heap_array(self):
        return self._heap_array

    @heap_array.setter
    def heap_array(self, heap_array):
        self._heap_array = heap_array

    # ------------------------------------------------------------------
    # Directly implemented (not abstract):
    # ------------------------------------------------------------------
    def insert(self, data):
        if data is None:
            raise ValueError("The heap does not accept None")
        self._heap_array.append(data)
        self._heapify_up(len(self._heap_array) - 1)

    def extract_root(self):
        if self.is_empty():
            raise IndexError("Can not extract from an empty heap")
        root = self._heap_array[0]
        last = self._heap_array.pop()
        if self._heap_array:
            self._heap_array[0] = last
            self._heapify_down(0)
        return root

    def peek_root(self):
        if self.is_empty():
            raise IndexError("Heap is empty")
        return self._heap_array[0]

    def is_empty(self):
        return len(self._heap_array) == 0

    def size(self):
        return len(self._heap_array)

    def empty(self):
        self._heap_array.clear()

    def build_heap(self, data):
        self._heap_array = list(data)
        for i in range(self._parent_index(len(self._heap_array) - 1), -1, -1):
            self._heapify_down(i)

    def __str__(self):
        return str(self._heap_array)

    # ------------------------------------------------------------------
    # Internal support methods (private/protected, shared by min and max):
    # ------------------------------------------------------------------
    def _parent_index(self, i):
        return (i - 1) // 2

    def _left_child_index(self, i):
        return 2 * i + 1

    def _right_child_index(self, i):
        return 2 * i + 2

    def _has_parent(self, i):
        return i > 0

    def _has_left_child(self, i):
        return self._left_child_index(i) < len(self._heap_array)

    def _has_right_child(self, i):
        return self._right_child_index(i) < len(self._heap_array)

    def _swap(self, i, j):
        self._heap_array[i], self._heap_array[j] = (
            self._heap_array[j],
            self._heap_array[i],
        )

    def _heapify_up(self, index):
        while self._has_parent(index) and self.has_priority(
            self._heap_array[index], self._heap_array[self._parent_index(index)]
        ):
            self._swap(index, self._parent_index(index))
            index = self._parent_index(index)

    def _heapify_down(self, index):
        while self._has_left_child(index):
            priority_child_index = self._left_child_index(index)
            if self._has_right_child(index) and self.has_priority(
                self._heap_array[self._right_child_index(index)],
                self._heap_array[self._left_child_index(index)],
            ):
                priority_child_index = self._right_child_index(index)
            if self.has_priority(
                self._heap_array[index], self._heap_array[priority_child_index]
            ):
                break
            self._swap(index, priority_child_index)
            index = priority_child_index

    # ------------------------------------------------------------------
    # Abstract method
    # ------------------------------------------------------------------
    @abstractmethod
    def has_priority(self, a, b):
        """Return True if 'a' should be higher up in the heap than 'b'."""
        pass