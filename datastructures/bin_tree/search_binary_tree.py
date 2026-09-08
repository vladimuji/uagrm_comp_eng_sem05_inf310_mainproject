"""
Module: search_binary_tree.py
Subject: INF310 - Data Structures II
Description: Binary Search Tree (BST), extending BinaryTree with
             order-respecting insertion and search, plus height,
             size and breadth (level-order) methods.

Author: Vladimir
"""

from collections import deque

from datastructures.bin_tree.binary_tree import BinaryTree


class SearchBinaryTree(BinaryTree):
    """Binary Search Tree: insert/search respect key order."""

    def insert(self, data):
        """Insert data respecting BST order (left < root < right)."""
        if data is None:
            raise ValueError("The tree does not accept None as a valid value.")

        if self.is_empty_tree():
            self.root = self.create_node(data)
            return

        self._insert_rec(self.root, data)

    def _insert_rec(self, current_node, data):
        if data < current_node.data:
            if self.is_empty_node(current_node.left_child):
                current_node.left_child = self.create_node(data)
            else:
                self._insert_rec(current_node.left_child, data)
        elif data > current_node.data:
            if self.is_empty_node(current_node.right_child):
                current_node.right_child = self.create_node(data)
            else:
                self._insert_rec(current_node.right_child, data)
        # If equal, do nothing (no duplicates allowed).

    def search(self, data):
        """Return the data if found (BST search), else None."""
        if data is None:
            raise ValueError("Data can't be None")
        return self._search_rec(self.root, data)

    def _search_rec(self, current_node, data):
        if self.is_empty_node(current_node):
            return None
        if data < current_node.data:
            return self._search_rec(current_node.left_child, data)
        if data > current_node.data:
            return self._search_rec(current_node.right_child, data)
        return current_node.data

    def has(self, data):
        """Return True if data exists in the tree (BST search)."""
        return self.search(data) is not None

    