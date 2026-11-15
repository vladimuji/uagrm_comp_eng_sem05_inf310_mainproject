"""
Module: bmway_tree.py
Subject: INF310 - Data Structures II
Description: BMWayNode and BMWayTree, the actual B-Tree implementation.
             Extends MWayNode / MWaySearchTree with the real B-Tree
             invariants: min/max keys per node, splits on overflow,
             merges on underflow. Mirrors the Java BMWayNode / BMWayTree
             classes.

Author: Vladimir
"""

import math

from datastructures.bin_tree.mway_search_tree import MWayNode, MWaySearchTree


class BMWayNode(MWayNode):
    """Node of a B-Tree: adds min/max key bounds on top of MWayNode."""

    def __init__(self, order):
        super().__init__(order)
        self._min_keys = math.ceil(order / 2) - 1  # typical B-Tree rule
        self._max_keys = order - 1

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def min_keys(self):
        return self._min_keys

    @property
    def max_keys(self):
        return self._max_keys

    # ------------------------------------------------------------------
    # Specific methods
    # ------------------------------------------------------------------
    def is_node_full(self):
        """Return True if the node reached the max allowed keys."""
        return len(self.keys) >= self._max_keys

    def is_overflow(self):
        """Return True if the node exceeded the max allowed keys."""
        return len(self.keys) > self._max_keys

    def is_node_minimum(self):
        """Return True if the node has min_keys or fewer keys."""
        return len(self.keys) <= self._min_keys

    def degree(self):
        """Return the current number of children."""
        return len(self.children)

    def insert_key(self, key):
        """Insert a key, keeping the keys list sorted."""
        self.keys.append(key)
        self.keys.sort()

    def delete_key(self, key):
        """Remove a key if it exists."""
        if key in self.keys:
            self.keys.remove(key)

    def get_left_child(self, index):
        """Return the left child relative to the key at position index."""
        if 0 <= index < len(self.children):
            return self.children[index]
        return None

    def get_right_child(self, index):
        """Return the right child relative to the key at position index."""
        if 0 <= index + 1 < len(self.children):
            return self.children[index + 1]
        return None


class BMWayTree(MWaySearchTree):
    """B-Tree: extends MWaySearchTree with real balancing rules."""

    def __init__(self, order):
        super().__init__(order)
        self.root = BMWayNode(order)  # root as a BMWayNode
        self._min_keys = math.ceil(order / 2) - 1
        self._max_keys = order - 1

    # ------------------------------------------------------------------
    # Specific B-Tree methods
    # ------------------------------------------------------------------
    def insert(self, data):
        if data is None:
            raise ValueError("The tree does not accept None.")
        if self.has(data):
            return  # no duplicates
        if self.root is None:
            self.root = BMWayNode(self.order)

        self._insert_recursive(self.root, data)

        if self.root.is_overflow():
            self._split_root()

    def _insert_recursive(self, node, data):
        if self.is_leaf(node):
            node.insert_key(data)
            self._increment_size()
            return

        i = 0
        while i < len(node.keys) and data > node.keys[i]:
            i += 1

        child = node.children[i]
        self._insert_recursive(child, data)

        if child.is_overflow():
            self._split_child(node, i)

    def _increment_size(self):
        self._size += 1

    def delete(self, data):
        if self.root is None or not self.has(data):
            return

        self._delete_recursive(self.root, data)

        # The root may end up empty after a merge: the tree shrinks
        if self.root.key_count() == 0 and not self.is_leaf(self.root):
            self.root = self.root.children[0]

    def _delete_recursive(self, node, data):
        i = 0
        while i < len(node.keys) and data > node.keys[i]:
            i += 1
        found = i < len(node.keys) and node.keys[i] == data

        if self.is_leaf(node):
            if found:
                node.keys.pop(i)
                self.decrement_size()
            return

        if found:
            # Internal node: replace by in-order successor, then delete
            # the successor from the right subtree
            child_index = i + 1
            successor = self._get_min_key(node.children[child_index])
            node.keys[i] = successor
            self._delete_recursive(node.children[child_index], successor)
        else:
            child_index = i
            self._delete_recursive(node.children[child_index], data)

        if node.children[child_index].key_count() < self._min_keys:
            self._fix_underflow(node, child_index)

    def search(self, data):
        return super().search(data)

    # ------------------------------------------------------------------
    # Balancing helpers
    # ------------------------------------------------------------------
    def _split_child(self, parent, index):
        """Split the full child at parent.children[index]."""
        full_node = parent.children[index]

        mid_index = full_node.key_count() // 2
        mid_key = full_node.keys[mid_index]

        left = BMWayNode(full_node.order)
        right = BMWayNode(full_node.order)

        for i in range(mid_index):
            left.keys.append(full_node.keys[i])
        for i in range(mid_index + 1, full_node.key_count()):
            right.keys.append(full_node.keys[i])

        if not self.is_leaf(full_node):
            left.children = list(full_node.children[:mid_index + 1])
            right.children = list(full_node.children[mid_index + 1:])

        # Insert mid_key and the new children into the parent, at the right position
        parent.keys.insert(index, mid_key)
        parent.children.pop(index)
        parent.children.insert(index, right)
        parent.children.insert(index, left)

    def _split_root(self):
        """Special case: the root overflowed (no parent to split into)."""
        old_root = self.root

        mid_index = old_root.key_count() // 2
        mid_key = old_root.keys[mid_index]

        left = BMWayNode(old_root.order)
        right = BMWayNode(old_root.order)

        for i in range(mid_index):
            left.keys.append(old_root.keys[i])
        for i in range(mid_index + 1, old_root.key_count()):
            right.keys.append(old_root.keys[i])

        if not self.is_leaf(old_root):
            left.children = list(old_root.children[:mid_index + 1])
            right.children = list(old_root.children[mid_index + 1:])

        new_root = BMWayNode(old_root.order)
        new_root.keys.append(mid_key)
        new_root.children.append(left)
        new_root.children.append(right)
        self.root = new_root

    def _fix_underflow(self, parent, index):
        """Child at parent.children[index] has too few keys:
        borrow from a sibling if it can spare one, else merge."""
        left = parent.children[index - 1] if index > 0 else None
        right = (
            parent.children[index + 1]
            if index + 1 < len(parent.children) else None
        )

        if left is not None and left.key_count() > self._min_keys:
            self._borrow_from_left(parent, index)
        elif right is not None and right.key_count() > self._min_keys:
            self._borrow_from_right(parent, index)
        elif left is not None:
            self._merge_children(parent, index - 1)
        else:
            self._merge_children(parent, index)

    def _borrow_from_left(self, parent, index):
        child = parent.children[index]
        left = parent.children[index - 1]
        child.keys.insert(0, parent.keys[index - 1])
        parent.keys[index - 1] = left.keys.pop()
        if left.children:
            child.children.insert(0, left.children.pop())

    def _borrow_from_right(self, parent, index):
        child = parent.children[index]
        right = parent.children[index + 1]
        child.keys.append(parent.keys[index])
        parent.keys[index] = right.keys.pop(0)
        if right.children:
            child.children.append(right.children.pop(0))

    def _merge_children(self, parent, index):
        """Merge children[index] and children[index + 1] with the
        separator key between them."""
        left = parent.children[index]
        right = parent.children[index + 1]
        left.keys.append(parent.keys.pop(index))
        left.keys.extend(right.keys)
        left.children.extend(right.children)
        parent.children.pop(index + 1)

    def _validate_btree(self):
        """Validate the B-Tree rules across every node."""
        return self._validate_recursive(self.root)

    def _validate_recursive(self, node):
        if node is None:
            return True

        if not self.is_leaf(node):
            for child in node.children:
                if not self._validate_recursive(child):
                    return False

        # Validate key count (root is exempt)
        if node is not self.root:
            if node.key_count() < self._min_keys or node.key_count() > self._max_keys:
                return False
        return True

    # ------------------------------------------------------------------
    # Auxiliary methods
    # ------------------------------------------------------------------
    def _get_min_key(self, node):
        if self.is_leaf(node):
            return node.keys[0]
        return self._get_min_key(node.children[0])

    def print_tree_recursive(self):
        self._print_tree_recursive(self.root, "", True)

    def _print_tree_recursive(self, node, indent, is_root):
        if node is None:
            return
        print(indent + ("ROOT -> " if is_root else "") + str(node.keys))
        if not self.is_leaf(node):
            children = node.children
            for i, child in enumerate(children):
                print(indent + "  |-- child[" + str(i) + "]: ", end="")
                self._print_tree_recursive(child, indent + "  ", False)