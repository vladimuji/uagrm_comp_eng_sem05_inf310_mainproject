"""
Module: search_binary_tree.py
Subject: INF310 - Data Structures II
Description: Binary Search Tree (BST), extending BinaryTree with
             order-respecting insertion and search, plus height,
             size and breadth (level-order) methods.

Author: Vladimir
"""

#from collections import deque

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

    def delete(self, data):
        """Delete data respecting BST order. Does nothing if not found."""
        if data is None:
            raise ValueError("Data can't be None")
        self.root = self._delete_rec(self.root, data)

    def _delete_rec(self, current_node, data):
        """Return the new root of this subtree after deleting data."""
        if self.is_empty_node(current_node):
            return current_node  # not found

        if data < current_node.data:
            current_node.left_child = self._delete_rec(
                current_node.left_child, data
            )
        elif data > current_node.data:
            current_node.right_child = self._delete_rec(
                current_node.right_child, data
            )
        else:
            # Case 1 and 2: leaf or one child -> replace by the child
            if self.is_empty_node(current_node.left_child):
                return current_node.right_child
            if self.is_empty_node(current_node.right_child):
                return current_node.left_child

            # Case 3: two children -> in-order successor swap
            successor = self._min_node(current_node.right_child)
            current_node.data = successor.data
            current_node.right_child = self._delete_rec(
                current_node.right_child, successor.data
            )
        return current_node

    def _min_node(self, node):
        while not self.is_empty_node(node.left_child):
            node = node.left_child
        return node

    def _max_node(self, node):
        while not self.is_empty_node(node.right_child):
            node = node.right_child
        return node

    def min(self):
        """Smallest data in the tree, or None if empty."""
        if self.is_empty_tree():
            return None
        return self._min_node(self.root).data

    def max(self):
        """Largest data in the tree, or None if empty."""
        if self.is_empty_tree():
            return None
        return self._max_node(self.root).data