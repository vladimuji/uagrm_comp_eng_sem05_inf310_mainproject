"""
Module: tic_tac_toe_strategy.py
Subject: INF310 - Data Structures II
Description: Tic-Tac-Toe strategy tree built with a plain Binary Tree
             using the Left-Child, Right-Sibling (LCRS) representation:

                 left_child  -> first possible next move (board state)
                 right_child -> next sibling alternative at the same
                                 decision point

             Each BinaryNode's data is a 3x3 board matrix. This models
             "strategy" because a node's set of possible next moves is
             encoded as a sibling chain hanging off its left_child, and
             choosing a move means walking/selecting inside that chain.

Author: Vladimir
"""

import sys
import copy

from pathlib import Path

# 1. Calculate the absolute path to the "project" root folder
# __file__ is this script -> .parent is "exercices" -> .parent.parent is "00-code"
project_root = Path(__file__).resolve().parent.parent

# 2. Add the "project" directory to Python's module search path
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# 3. Now you can safely import using standard dot notation
from datastructures.bin_tree.binary_tree import BinaryNode


class TicTacToeStrategyTree:
    """Generates and walks a Tic-Tac-Toe decision tree using the
    Left-Child, Right-Sibling binary representation of a general tree."""

    def __init__(self):
        self._root = BinaryNode(TicTacToeStrategyTree.empty_matrix())

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, node):
        self._root = node

    # ------------------------------------------------------------------
    # Board helpers
    # ------------------------------------------------------------------
    @staticmethod
    def empty_matrix():
        """Return a fresh empty 3x3 board (all cells set to None)."""
        return [[None for _ in range(3)] for _ in range(3)]

    # ------------------------------------------------------------------
    # LCRS tree building
    # ------------------------------------------------------------------
    def generate_children(self, node, mark):
        """Generate every possible next board (one per empty cell) and
        chain them as: node.left_child = first option, then each option
        links to the next one through right_child (sibling chain)."""
        previous_sibling = None
        first_child = None

        for row in range(3):
            for column in range(3):
                if node.data[row][column] is None:
                    child_matrix = copy.deepcopy(node.data)
                    child_matrix[row][column] = mark
                    child_node = BinaryNode(child_matrix)

                    if first_child is None:
                        first_child = child_node
                    else:
                        previous_sibling.right_child = child_node

                    previous_sibling = child_node

        node.left_child = first_child
        return first_child

    def is_leaf(self, node):
        """A node is a leaf if it has no generated options yet."""
        return node.left_child is None

    def get_children_list(self, node):
        """Walk the sibling chain starting at node.left_child and
        return every alternative as a plain list (handy for display)."""
        options = []
        current_sibling = node.left_child
        while current_sibling is not None:
            options.append(current_sibling)
            current_sibling = current_sibling.right_child
        return options

    # ------------------------------------------------------------------
    # Decision making (the "strategy")
    # ------------------------------------------------------------------
    def choose_move(self, node):
        """Simplest possible strategy: always take the first generated
        option (node.left_child). Easy to defend, easy to upgrade later
        (e.g. block the opponent, prefer the center, etc.)."""
        return node.left_child

    # ------------------------------------------------------------------
    # Game rules
    # ------------------------------------------------------------------
    @staticmethod
    def get_winner(matrix):
        """Return 'X', 'O' or None depending on whether someone completed
        a row, a column or a diagonal."""
        lines = []
        lines.extend(matrix)  # rows
        lines.extend([[matrix[r][c] for r in range(3)] for c in range(3)])  # columns
        lines.append([matrix[i][i] for i in range(3)])  # main diagonal
        lines.append([matrix[i][2 - i] for i in range(3)])  # anti diagonal

        for line in lines:
            if line[0] is not None and line[0] == line[1] == line[2]:
                return line[0]
        return None

    @staticmethod
    def is_full(matrix):
        return all(cell is not None for row in matrix for cell in row)

    # ------------------------------------------------------------------
    # Console helpers
    # ------------------------------------------------------------------
    @staticmethod
    def print_board(matrix):
        rows = [" | ".join(cell or " " for cell in row) for row in matrix]
        print(("\n" + "-" * 9 + "\n").join(rows))

    @staticmethod
    def parse_cell(text):
        """Parse a cell like 'A2' into (row, column) zero-based indexes.
        Rows are letters A-C, columns are numbers 1-3."""
        text = text.strip().upper()
        if len(text) != 2 or text[0] not in "ABC" or text[1] not in "123":
            raise ValueError("Use a letter A-C followed by a number 1-3, e.g. B2")
        row = ord(text[0]) - ord("A")
        column = int(text[1]) - 1
        return row, column


def play():
    """Simple console game: human plays 'X', machine plays 'O' and
    always chooses its first generated option in the strategy tree."""
    tree = TicTacToeStrategyTree()
    current_node = tree.root

    while True:
        TicTacToeStrategyTree.print_board(current_node.data)

        winner = TicTacToeStrategyTree.get_winner(current_node.data)
        if winner is not None:
            print(f"\n{winner} wins!")
            break
        if TicTacToeStrategyTree.is_full(current_node.data):
            print("\nIt's a draw!")
            break

        # ---- Human turn (X) ----
        while True:
            try:
                row, column = TicTacToeStrategyTree.parse_cell(
                    input("\nYour move (e.g. A2): ")
                )
                if current_node.data[row][column] is not None:
                    print("That cell is already taken.")
                    continue
                break
            except ValueError as error:
                print(error)

        current_node.data[row][column] = "X"

        TicTacToeStrategyTree.print_board(current_node.data)
        winner = TicTacToeStrategyTree.get_winner(current_node.data)
        if winner is not None:
            print(f"\n{winner} wins!")
            break
        if TicTacToeStrategyTree.is_full(current_node.data):
            print("\nIt's a draw!")
            break

        # ---- Machine turn (O) ----
        tree.generate_children(current_node, "O")
        current_node = tree.choose_move(current_node)
        print("\nMachine plays...")


if __name__ == "__main__":
    play()