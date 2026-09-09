"""
Module: mway_search_tree.py
Subject: INF310 - Data Structures II
Description: MWayNode and MWaySearchTree, a generic M-way search tree
             (no balancing discipline -- BMWayTree adds the real
             B-Tree invariants on top of this). Mirrors the Java
             MWayNode / MWaySearchTree classes.

Author: Vladimir
"""

from collections import deque


class MWayNode:
    """Node of an M-way search tree: holds a sorted list of keys and
    up to order + 1 children.
    """

    def __init__(self, order):
        self._order = order
        self._keys = []
        self._children = []

    # ------------------------------------------------------------------
    # Properties (Pythonic getters and setters)
    # ------------------------------------------------------------------
    @property
    def keys(self):
        return self._keys

    @keys.setter
    def keys(self, keys):
        self._keys = keys

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children):
        self._children = children

    @property
    def order(self):
        return self._order

    def is_full(self):
        """Return True if this node reached the max allowed keys (order - 1)."""
        return len(self._keys) >= (self._order - 1)

    def key_count(self):
        """Return how many keys are stored in this node."""
        return len(self._keys)


class MWaySearchTree:
    """Generic M-way search tree (matches Java's IBinaryTree public API)."""

    def __init__(self, order):
        self._order = order
        self._root = None
        self._size = 0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def order(self):
        return self._order

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, node):
        self._root = node

    def is_empty_node(self, node):
        return node is None

    def is_leaf(self, node):
        if node is None:
            return False
        for child in node.children:
            if not self.is_empty_node(child):
                return False
        return True

    # ------------------------------------------------------------------
    # Interface methods
    # ------------------------------------------------------------------
    def insert(self, data):
        if self._root is None:
            self._root = MWayNode(self._order)
            self._root.keys.append(data)
            self._size += 1
            return
        self._insert_recursive(self._root, data)

    def _insert_recursive(self, node, data):
        if self.is_leaf(node) and not node.is_full():
            node.keys.append(data)
            node.keys.sort()
            self._size += 1
            return

        i = 0
        while i < len(node.keys) and data > node.keys[i]:
            i += 1

        # Fill with None placeholders up to index i
        while len(node.children) <= i:
            node.children.append(None)

        # Create the real node only if it does not exist yet
        if node.children[i] is None:
            node.children[i] = MWayNode(self._order)

        self._insert_recursive(node.children[i], data)

    def delete(self, data):
        if self._root is None:
            return
        self._delete_recursive(self._root, data)

    def _delete_recursive(self, node, data):
        if node is None:
            return

        # 1. Look for the key inside this node
        index = -1
        for i, key in enumerate(node.keys):
            if key == data:
                index = i
                break

        # 2. If the key is in this node
        if index != -1:
            if self.is_leaf(node):
                node.keys.pop(index)
                self._size -= 1
            else:
                # Replace with successor (smallest key of the right subtree)
                successor_child = node.children[index + 1]
                successor_key = self._get_min_key(successor_child)
                node.keys[index] = successor_key
                self._delete_recursive(successor_child, successor_key)
            return

        # 3. If the key is not in this node, go down to the right child
        i = 0
        while i < len(node.keys) and data > node.keys[i]:
            i += 1

        if i < len(node.children):
            self._delete_recursive(node.children[i], data)

    def decrement_size(self):
        self._size -= 1

    def _get_min_key(self, node):
        if node is None:
            return None
        if self.is_leaf(node):
            return node.keys[0]
        return self._get_min_key(node.children[0])

    def search(self, data):
        return self._search_recursive(self._root, data)

    def _search_recursive(self, node, data):
        if node is None:
            return None

        for key in node.keys:
            if key == data:
                return key

        i = 0
        while i < len(node.keys) and data > node.keys[i]:
            i += 1

        if i < len(node.children):
            return self._search_recursive(node.children[i], data)

        return None

    def has(self, data):
        return self.search(data) is not None

    def high(self):
        return self._height_recursive(self._root)

    def _height_recursive(self, node):
        if node is None:
            return 0
        if self.is_leaf(node):
            return 1

        max_height = 0
        for child in node.children:
            max_height = max(max_height, self._height_recursive(child))
        return max_height + 1

    def size(self):
        return self._size

    def is_empty_tree(self):
        return self._root is None

    def level(self, data):
        return self._level_recursive(self._root, data, 0)

    def _level_recursive(self, node, data, level):
        if node is None:
            return -1

        for key in node.keys:
            if key == data:
                return level

        i = 0
        while i < len(node.keys) and data > node.keys[i]:
            i += 1

        if i < len(node.children):
            return self._level_recursive(node.children[i], data, level + 1)

        return -1

    def empty(self):
        self._root = None
        self._size = 0

    def in_order(self):
        result = []
        self._in_order_recursive(self._root, result)
        return result

    def _in_order_recursive(self, node, result):
        if node is None:
            return

        for i in range(len(node.keys)):
            if i < len(node.children):
                self._in_order_recursive(node.children[i], result)
            result.append(node.keys[i])

        if len(node.children) > len(node.keys):
            self._in_order_recursive(node.children[len(node.keys)], result)

    def pre_order(self):
        result = []
        self._pre_order_recursive(self._root, result)
        return result

    def _pre_order_recursive(self, node, result):
        if node is None:
            return

        result.extend(node.keys)
        for child in node.children:
            self._pre_order_recursive(child, result)

    def post_order(self):
        result = []
        self._post_order_recursive(self._root, result)
        return result

    def _post_order_recursive(self, node, result):
        if node is None:
            return

        for child in node.children:
            self._post_order_recursive(child, result)
        result.extend(node.keys)

    def iteration_by_levels(self):
        result = []
        if self._root is None:
            return result

        nodes_queue = deque([self._root])
        while nodes_queue:
            current = nodes_queue.popleft()
            result.extend(current.keys)
            for child in current.children:
                nodes_queue.append(child)

        return result