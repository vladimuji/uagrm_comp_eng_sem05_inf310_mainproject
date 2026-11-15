
"""
Module: bplus_tree.py
Subject: INF310 - Data Structures II
Description: BPlusNode and BPlusTree. B+ Tree: all keys live in the
             leaves, internal nodes only hold separators (copies),
             and the leaves are linked through next_leaf.
             Extends MWayNode / MWaySearchTree.

Author: Vladimir
"""

import bisect

from datastructures.bin_tree.mway_search_tree import MWayNode, MWaySearchTree


class BPlusNode(MWayNode):
    """Node of a B+ Tree: internal (separators) or leaf (keys)."""

    def __init__(self, order, is_leaf=True):
        super().__init__(order)
        self._is_leaf = is_leaf
        self._next_leaf = None

    # ------------------------------------------------------------------
    # Properties (Pythonic getters and setters)
    # ------------------------------------------------------------------
    @property
    def is_leaf(self):
        return self._is_leaf

    @is_leaf.setter
    def is_leaf(self, value):
        self._is_leaf = value

    @property
    def next_leaf(self):
        return self._next_leaf

    @next_leaf.setter
    def next_leaf(self, node):
        self._next_leaf = node

    # ------------------------------------------------------------------
    # Specific methods
    # ------------------------------------------------------------------
    def is_overflow(self):
        return len(self.keys) > self.order - 1

    def degree(self):
        return len(self.children)


class BPlusTree(MWaySearchTree):
    """B+ Tree of the given order (max children per node)."""

    def __init__(self, order=4):
        if order < 3:
            raise ValueError("Order must be at least 3")
        super().__init__(order)
        self._root = BPlusNode(order, True)

    # ------------------------------------------------------------------
    # Structure rules
    # ------------------------------------------------------------------
    def is_leaf(self, node):
        return node is not None and node.is_leaf

    def _min_keys_of(self, node):
        if node.is_leaf:
            return self.order // 2
        return (self.order + 1) // 2 - 1

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def _find_leaf(self, key):
        node = self._root
        while not node.is_leaf:
            node = node.children[bisect.bisect_right(node.keys, key)]
        return node

    def search(self, data):
        if data is None:
            raise ValueError("Data can't be None")
        leaf = self._find_leaf(data)
        i = bisect.bisect_left(leaf.keys, data)
        if i < len(leaf.keys) and leaf.keys[i] == data:
            return leaf.keys[i]
        return None

    def has(self, data):
        return self.search(data) is not None

    def range_search(self, low, high):
        """Keys in [low, high], walking the linked leaves."""
        result = []
        leaf = self._find_leaf(low)
        while leaf is not None:
            for key in leaf.keys:
                if key > high:
                    return result
                if key >= low:
                    result.append(key)
            leaf = leaf.next_leaf
        return result

    def min(self):
        return None if self._size == 0 else self._first_leaf().keys[0]

    def max(self):
        if self._size == 0:
            return None
        node = self._root
        while not node.is_leaf:
            node = node.children[-1]
        return node.keys[-1]

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------
    def insert(self, data):
        if data is None:
            raise ValueError("The tree does not accept None.")
        if self.has(data):
            return  # no duplicates
        split = self._insert_rec(self._root, data)
        self._size += 1
        if split is not None:
            promoted, right = split
            new_root = BPlusNode(self.order, False)
            new_root.keys = [promoted]
            new_root.children = [self._root, right]
            self._root = new_root

    def _insert_rec(self, node, data):
        """Return (promoted_key, new_right_node) if node split."""
        if node.is_leaf:
            bisect.insort(node.keys, data)
            return self._split_leaf(node) if node.is_overflow() else None

        i = bisect.bisect_right(node.keys, data)
        split = self._insert_rec(node.children[i], data)
        if split is None:
            return None
        promoted, right = split
        node.keys.insert(i, promoted)
        node.children.insert(i + 1, right)
        return self._split_internal(node) if node.is_overflow() else None

    def _split_leaf(self, node):
        mid = len(node.keys) // 2
        right = BPlusNode(self.order, True)
        right.keys = node.keys[mid:]
        node.keys = node.keys[:mid]
        right.next_leaf = node.next_leaf
        node.next_leaf = right
        return right.keys[0], right  # COPIED up (stays in the leaf)

    def _split_internal(self, node):
        mid = len(node.keys) // 2
        promoted = node.keys[mid]  # MOVED up (leaves the node)
        right = BPlusNode(self.order, False)
        right.keys = node.keys[mid + 1:]
        right.children = node.children[mid + 1:]
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]
        return promoted, right

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def delete(self, data):
        if data is None:
            raise ValueError("Data can't be None")
        if not self.has(data):
            return
        self._delete_rec(self._root, data)
        # The root may end up with no keys: the tree shrinks
        if not self._root.is_leaf and self._root.key_count() == 0:
            self._root = self._root.children[0]

    def _delete_rec(self, node, data):
        if node.is_leaf:
            i = bisect.bisect_left(node.keys, data)
            node.keys.pop(i)
            self.decrement_size()
            return

        i = bisect.bisect_right(node.keys, data)
        child = node.children[i]
        self._delete_rec(child, data)
        # Separators may stay stale after a delete: they still route
        # correctly, so they are not touched.
        if child.key_count() < self._min_keys_of(child):
            self._fix_underflow(node, i)

    def _fix_underflow(self, parent, index):
        left = parent.children[index - 1] if index > 0 else None
        right = (
            parent.children[index + 1]
            if index + 1 < len(parent.children) else None
        )
        child = parent.children[index]
        minimum = self._min_keys_of(child)

        if left is not None and left.key_count() > minimum:
            self._borrow_from_left(parent, index)
        elif right is not None and right.key_count() > minimum:
            self._borrow_from_right(parent, index)
        elif left is not None:
            self._merge_children(parent, index - 1)
        else:
            self._merge_children(parent, index)

    def _borrow_from_left(self, parent, index):
        child = parent.children[index]
        left = parent.children[index - 1]
        if child.is_leaf:
            child.keys.insert(0, left.keys.pop())
            parent.keys[index - 1] = child.keys[0]
        else:
            child.keys.insert(0, parent.keys[index - 1])
            parent.keys[index - 1] = left.keys.pop()
            child.children.insert(0, left.children.pop())

    def _borrow_from_right(self, parent, index):
        child = parent.children[index]
        right = parent.children[index + 1]
        if child.is_leaf:
            child.keys.append(right.keys.pop(0))
            parent.keys[index] = right.keys[0]
        else:
            child.keys.append(parent.keys[index])
            parent.keys[index] = right.keys.pop(0)
            child.children.append(right.children.pop(0))

    def _merge_children(self, parent, index):
        """Merge children[index] and children[index + 1]."""
        left = parent.children[index]
        right = parent.children[index + 1]
        separator = parent.keys.pop(index)
        if left.is_leaf:
            left.keys.extend(right.keys)  # separator is just dropped
            left.next_leaf = right.next_leaf
        else:
            left.keys.append(separator)
            left.keys.extend(right.keys)
            left.children.extend(right.children)
        parent.children.pop(index + 1)

    # ------------------------------------------------------------------
    # Traversals / info
    # ------------------------------------------------------------------
    def _first_leaf(self):
        node = self._root
        while not node.is_leaf:
            node = node.children[0]
        return node

    def in_order(self):
        """All keys in order, following the leaf chain."""
        result = []
        leaf = self._first_leaf()
        while leaf is not None:
            result.extend(leaf.keys)
            leaf = leaf.next_leaf
        return result

    def high(self):
        height, node = 1, self._root
        while not node.is_leaf:
            node = node.children[0]
            height += 1
        return height

    def level(self, data):
        """Depth of the leaf holding data (root = 0), or -1."""
        node, depth = self._root, 0
        while not node.is_leaf:
            node = node.children[bisect.bisect_right(node.keys, data)]
            depth += 1
        return depth if data in node.keys else -1

    def empty(self):
        self._root = BPlusNode(self.order, True)
        self._size = 0

    # pre_order, post_order and iteration_by_levels are inherited:
    # they also show the separators of the internal nodes.

    # ------------------------------------------------------------------
    # Validation (for tests)
    # ------------------------------------------------------------------
    def _validate_bplus(self):
        depths = set()

        def check(node, low, high, depth):
            if node is not self._root:
                if not (self._min_keys_of(node) <= node.key_count()
                        <= self.order - 1):
                    return False
            if node.keys != sorted(node.keys):
                return False
            if any((low is not None and k < low)
                   or (high is not None and k >= high)
                   for k in node.keys):
                return False
            if node.is_leaf:
                depths.add(depth)
                return True
            if len(node.children) != len(node.keys) + 1:
                return False
            for i, child in enumerate(node.children):
                lo = node.keys[i - 1] if i > 0 else low
                hi = node.keys[i] if i < len(node.keys) else high
                if not check(child, lo, hi, depth + 1):
                    return False
            return True

        ok = check(self._root, None, None, 0)
        keys = self.in_order()
        return ok and len(depths) == 1 and keys == sorted(set(keys))