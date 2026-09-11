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
        if self.root is None:
            return

        self._delete_recursive(self.root, data)

        # Adjust the root if it ends up empty
        if self.root.key_count() == 0 and not self.is_leaf(self.root):
            self.root = self.root.children[0]

    def _delete_recursive(self, node, data):
        if node is None:
            return

        # Look for the key in this node
        index = -1
        for i, key in enumerate(node.keys):
            if key == data:
                index = i
                break

        if index != -1:
            # Case 1: key found
            if self.is_leaf(node):
                node.delete_key(data)
                self.decrement_size()
            else:
                # Case 2: internal node -> replace with successor
                successor_child = node.get_right_child(index)
                successor_key = self._get_min_key(successor_child)
                node.keys[index] = successor_key
                self._delete_recursive(successor_child, successor_key)
        else:
            # Case 3: key not here -> go down to the right child
            i = 0
            while i < len(node.keys) and data > node.keys[i]:
                i += 1

            if i < len(node.children):
                child = node.children[i]
                self._delete_recursive(child, data)

                # Balance: if the child ended up below min_keys
                if child.key_count() < self._min_keys:
                    self._merge_node(child)

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

    def _merge_node(self, node):
        """Merge an underflowed node with a sibling."""
        parent = self._find_parent(self.root, node)
        if parent is None:
            return  # it's the root, nothing to merge into

        index = parent.children.index(node)

        # Try to merge with the left sibling
        if index > 0:
            left_sibling = parent.children[index - 1]
            separator_key = parent.keys[index - 1]

            left_sibling.keys.append(separator_key)
            left_sibling.keys.extend(node.keys)
            left_sibling.children.extend(node.children)

            parent.keys.pop(index - 1)
            parent.children.pop(index)
        # If there's no left sibling, merge with the right one
        elif index < len(parent.children) - 1:
            right_sibling = parent.children[index + 1]
            separator_key = parent.keys[index]

            node.keys.append(separator_key)
            node.keys.extend(right_sibling.keys)
            node.children.extend(right_sibling.children)

            parent.keys.pop(index)
            parent.children.pop(index + 1)

        # If the parent ends up below min_keys, apply recursively
        if parent is not self.root and parent.key_count() < self._min_keys:
            self._merge_node(parent)

    def _find_parent(self, current, target):
        """Find the parent of target, searching from current downward."""
        if current is None or self.is_leaf(current):
            return None

        for child in current.children:
            if child is target:
                return current
            result = self._find_parent(child, target)
            if result is not None:
                return result
        return None

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