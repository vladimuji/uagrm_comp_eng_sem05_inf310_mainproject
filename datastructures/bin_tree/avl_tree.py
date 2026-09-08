"""
Module: avl_tree.py
Subject: INF310 - Data Structures II
Description: AVL Tree (self-balancing Binary Search Tree), extending
             BinaryTree with height-aware insertion, deletion and
             rotations. Mirrors the Java AVLTree class.

Author: Vladimir
"""

from datastructures.bin_tree.binary_tree import BinaryNode, BinaryTree


class AVLNode(BinaryNode):
    """Node of an AVLTree: adds a height attribute to BinaryNode."""

    def __init__(self, data):
        super().__init__(data)
        self._height = 1

    # ------------------------------------------------------------------
    # Properties (Pythonic getters and setters)
    # ------------------------------------------------------------------
    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height


class AVLTree(BinaryTree):
    """AVL Tree: self-balancing Binary Search Tree.

    Reused as-is (inherited without changes):
    search, has, size, is_empty_tree, empty, level,
    in_order / pre_order / post_order / iteration_by_levels.
    """

    # ------------------------------------------------------------------
    # OVERRIDE METHODS
    # ------------------------------------------------------------------
    def insert(self, data):
        if data is None:
            raise ValueError(
                "The tree does not accept None as a valid value."
            )
        self.root = self._insert_avl(self.root, data)

    def _insert_avl(self, node, data):
        if self.is_empty_node(node):
            return self.create_node(data)
        if data < node.data:
            node.left_child = self._insert_avl(node.left_child, data)
        elif data > node.data:
            node.right_child = self._insert_avl(node.right_child, data)
        else:
            return node  # no duplicates
        return self._rebalance(node)

    def delete(self, data):
        if data is None:
            raise ValueError("Not None allowed in the Tree")
        self.root = self._delete_avl(self.root, data)

    def _delete_avl(self, node, data):
        if self.is_empty_node(node):
            print("Data " + str(data) + " not found in the Tree")
            return node
        if data < node.data:
            node.left_child = self._delete_avl(node.left_child, data)
        elif data > node.data:
            node.right_child = self._delete_avl(node.right_child, data)
        else:
            if self.is_empty_node(node.left_child):
                return node.right_child
            elif self.is_empty_node(node.right_child):
                return node.left_child
            successor = self._min_node(node.right_child)
            node.data = successor.data
            node.right_child = self._delete_avl(
                node.right_child, successor.data
            )
        return self._rebalance(node)

    def _min_node(self, node):
        while not self.is_empty_node(node.left_child):
            node = node.left_child
        return node

    def create_node(self, data):
        return AVLNode(data)

    def print_tree_recursive(self):
        self._print_tree_recursive(self.root, "", False)

    def _print_tree_recursive(self, node, indent, is_right):
        if node is None:
            return
        self._print_tree_recursive(
            node.right_child,
            indent + ("     " if is_right else "|    "),
            True,
        )
        print(
            indent + "|-- " + str(node.data)
            + " (h=" + str(self._get_height(node))
            + ", fb=" + str(self._get_balance_factor(node)) + ")"
        )
        self._print_tree_recursive(
            node.left_child,
            indent + ("|    " if is_right else "     "),
            False,
        )

    def high(self):
        return self._get_height(self.root)

    # ------------------------------------------------------------------
    # NEW METHODS
    # ------------------------------------------------------------------
    def _get_height(self, node):
        return 0 if node is None else node.height

    def _get_balance_factor(self, node):
        return (
            self._get_height(node.left_child)
            - self._get_height(node.right_child)
        )

    def _update_height(self, node):
        left_height = self._get_height(node.left_child)
        right_height = self._get_height(node.right_child)
        node.height = 1 + max(left_height, right_height)

    def _rebalance(self, node):
        self._update_height(node)
        balance_factor = self._get_balance_factor(node)

        if balance_factor > 1:
            if self._get_balance_factor(node.left_child) < 0:
                return self._left_right_double_rotation(node)
            return self._right_simple_rotation(node)
        if balance_factor < -1:
            if self._get_balance_factor(node.right_child) > 0:
                return self._right_left_double_rotation(node)
            return self._left_simple_rotation(node)
        return node

    def _right_simple_rotation(self, node):
        new_root = node.left_child
        node.left_child = new_root.right_child
        new_root.right_child = node

        self._update_height(node)
        self._update_height(new_root)

        return new_root

    def _left_simple_rotation(self, node):
        new_root = node.right_child
        node.right_child = new_root.left_child
        new_root.left_child = node

        self._update_height(node)
        self._update_height(new_root)

        return new_root

    def _left_right_double_rotation(self, node):
        node.left_child = self._left_simple_rotation(node.left_child)
        return self._right_simple_rotation(node)

    def _right_left_double_rotation(self, node):
        node.right_child = self._right_simple_rotation(node.right_child)
        return self._left_simple_rotation(node)

    def is_balanced(self):
        return self._is_balanced(self.root)

    def _is_balanced(self, node):
        if self.is_empty_node(node):
            return True
        balance_factor = self._get_balance_factor(node)
        if abs(balance_factor) > 1:
            return False
        return (
            self._is_balanced(node.left_child)
            and self._is_balanced(node.right_child)
        )
