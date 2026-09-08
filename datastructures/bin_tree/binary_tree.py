"""
Module: binary_tree.py
Subject: INF310 - Data Structures II
Description: Basic Binary Tree structure, with its node class and
             properties (getters/setters), following PEP8 standards.

Author: Vladimir
"""

from collections import deque


class BinaryNode:
    """Represents a node inside a Binary Tree."""

    def __init__(self, data):
        self._data = data
        self._left_child = None
        self._right_child = None

    # ------------------------------------------------------------------
    # Properties (Pythonic getters and setters)
    # ------------------------------------------------------------------
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def left_child(self):
        return self._left_child

    @left_child.setter
    def left_child(self, node):
        self._left_child = node

    @property
    def right_child(self):
        return self._right_child

    @right_child.setter
    def right_child(self, node):
        self._right_child = node

    def __str__(self):
        return str(self._data)


class BinaryTree:
    """Basic Binary Tree structure (no insertion order enforced)."""

    def __init__(self):
        self._root = None
        self._empty_node = None

    # ------------------------------------------------------------------
    # Properties (Pythonic getters and setters)
    # ------------------------------------------------------------------
    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, node):
        self._root = node

    @property
    def empty_node(self):
        return self._empty_node

    # ------------------------------------------------------------------
    # Support methods (used by subclasses)
    # ------------------------------------------------------------------
    def is_empty_node(self, node):
        """Return True if the given node is the empty node (None)."""
        return node is self._empty_node

    def is_empty_tree(self):
        """Return True if the tree has no root."""
        return self._root is None

    def create_node(self, data):
        """Create and return a new BinaryNode with the given data."""
        return BinaryNode(data)

    def is_leaf(self, node):
        """Return True if the node has no children (left nor right)."""
        return (
            self.is_empty_node(node.left_child)
            and self.is_empty_node(node.right_child)
        )

    def insert(self, data):
        """Insert data at the first empry spot found in level-order"""
        if data is None:
            raise ValueError("The tree does not accept None as a valid value.")

        if self.is_empty_tree():
            self._root = self.create_node(data)
            return

        nodes_queue = deque([self._root])
        while nodes_queue:
            node_in_turn = nodes_queue.popleft()
            if not self.is_empty_node(node_in_turn.left_child):
                nodes_queue.append(node_in_turn.left_child)
            else:
                node_in_turn.left_child = self.create_node(data)
                return

            if not self.is_empty_node(node_in_turn.right_child):
                nodes_queue.append(node_in_turn.right_child)
            else:
                node_in_turn.right_child = self.create_node(data)
                return


    def search(self, data):
        """Return the data if found in the tree (levell-order search), else None."""
        if data is None:
            raise ValueError("Data can't be None")

        if self.is_empty_tree():
            return None

        nodes_queue = deque([self._root])
        while nodes_queue:
            node_in_turn = nodes_queue.popleft()
            if node_in_turn.data == data:
                return node_in_turn.data

            if not self.is_empty_node(node_in_turn.left_child):
                nodes_queue.append(node_in_turn.left_child)

            if not self.is_empty_node(node_in_turn.right_child):
                nodes_queue.append(node_in_turn.right_child)

        return None

    def has(self, data):
        """Return True if the data exists in the tree (own level-order traversal)."""
        if data is None:
            raise ValueError("Data can't be None")

        if self.is_empty_tree():
            return False

        nodes_queue = deque([self._root])
        while nodes_queue:
            node_in_turn = nodes_queue.popleft()
            if node_in_turn.data == data:
                return True

            if not self.is_empty_node(node_in_turn.left_child):
                nodes_queue.append(node_in_turn.left_child)

            if not self.is_empty_node(node_in_turn.right_child):
                nodes_queue.append(node_in_turn.right_child)

        return False

    def high(self):
        """Return the height of the tree (0 for an empty tree)."""
        return self._high_rec(self.root)

    def _high_rec(self, current_node):
        if self.is_empty_node(current_node):
            return 0
        left_high = self._high_rec(current_node.left_child)
        right_high = self._high_rec(current_node.right_child)
        return 1 + max(left_high, right_high)

    def size(self):
        """Return the total number of nodes in the tree ('cantidad')."""
        return self._size_rec(self.root)

    def _size_rec(self, current_node):
        if self.is_empty_node(current_node):
            return 0
        return (
            1
            + self._size_rec(current_node.left_child)
            + self._size_rec(current_node.right_child)
        )

    def iteration_by_levels(self):
        """Return list of data in level-order (breadth / 'amplitud')."""
        iteration = []
        if self.is_empty_tree():
            return iteration

        nodes_queue = deque([self.root])
        while nodes_queue:
            node_in_turn = nodes_queue.popleft()
            iteration.append(node_in_turn.data)

            if not self.is_empty_node(node_in_turn.left_child):
                nodes_queue.append(node_in_turn.left_child)

            if not self.is_empty_node(node_in_turn.right_child):
                nodes_queue.append(node_in_turn.right_child)

        return iteration

    def pre_order(self):
        """Return list of data in pre-order (root, left, right)."""
        iteration = []
        self._pre_order_rec(self._root, iteration)
        return iteration

    def _pre_order_rec(self, current_node, iteration):
        if self.is_empty_node(current_node):
            return

        iteration.append(current_node.data)
        self._pre_order_rec(current_node.left_child, iteration)
        self._pre_order_rec(current_node.right_child, iteration)

    def _pre_order_iter(self):
        """Iterative pre-order using an explicit stack."""
        iteration = []
        if self.is_empty_tree():
            return iteration

        nodes_stack = [self._root]
        while nodes_stack:
            node_in_turn = nodes_stack.pop()
            iteration.append(node_in_turn.data)

            if not self.is_empty_node(node_in_turn.right_child):
                nodes_stack.append(node_in_turn.right_child)

            if not self.is_empty_node(node_in_turn.left_child):
                nodes_stack.append(node_in_turn.left_child)

        return iteration

    def in_order(self):
        """Return list of data in in-order (left, root, right)."""
        iteration = []
        self._in_order_rec(self._root, iteration)
        return iteration

    def _in_order_rec(self, current_node, iteration):
        if self.is_empty_node(current_node):
            return

        self._in_order_rec(current_node.left_child, iteration)
        iteration.append(current_node.data)
        self._in_order_rec(current_node.right_child, iteration)

    def _in_order_iter(self):
        """Iterative in-order using an explicit stack (go-left-then-visit-pattern)."""
        iteration = []
        stack = []
        current = self._root
        while stack or not self.is_empty_node(current):
            while not self.is_empty_node(current):
                stack.append(current)
                current = current.left_child
            current = stack.pop()
            iteration.append(current.data)
            current = current.right_child

        return iteration

    def post_order(self):
        """Return list of data in post-order (left, right, root)."""
        iteration = []
        self._post_order_rec(self._root, iteration)
        return iteration

    def _post_order_rec(self, current_node, iteration):
        if self.is_empty_node(current_node):
            return

        self._post_order_rec(current_node.left_child, iteration)
        self._post_order_rec(current_node.right_child, iteration)
        iteration.append(current_node.data)

    def _post_order_iter(self):
        """Iterative post-order using an explicit stack with right-child tracking."""
        iteration = []
        if self.is_empty_tree():
            return iteration

        nodes_stack = []
        node_in_turn = self._root
        self._insert_on_stack_to_post_order(node_in_turn, nodes_stack)

        while nodes_stack:
            node_in_turn = nodes_stack.pop()
            iteration.append(node_in_turn.data)

            if nodes_stack:
                top_node = nodes_stack[-1]
                if not self.is_empty_node(top_node.right_child):
                    if node_in_turn is not top_node.right_child:
                        self._insert_on_stack_to_post_order(top_node.right_child, nodes_stack)

        return iteration

    def _insert_on_stack_to_post_order(self, node_in_turn, nodes_stack):
        """Push nodes going left-first (falling back to right) until empty."""
        while not self.is_empty_node(node_in_turn):
            nodes_stack.append(node_in_turn)
            if not self.is_empty_node(node_in_turn.left_child):
                node_in_turn = node_in_turn.left_child
            else:
                node_in_turn = node_in_turn.right_child 

    def print_tree_recursive(self):
        """Print the tree to console, right subtree on top, left on bottom."""
        self._print_tree_recursive(self._root, "", False)

    def _print_tree_recursive(self, node, indent, is_right):
        if node is None:
            return
        self._print_tree_recursive(
            node.right_child, indent + ("    " if is_right else "|   "), True
        )
        print(indent + "|-- " + str(node.data))
        self._print_tree_recursive(
            node.left_child, indent + ("|   " if is_right else "    "), False
        )