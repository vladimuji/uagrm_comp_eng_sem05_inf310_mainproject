"""
Module: game_model.py
Subject: INF310 - Data Structures II
Description: Tic-Tac-Toe game state and rules (MVC Model).
             Supports make/undo moves for Backtracking.
"""


class GameModel:
    """3x3 board: each cell is None, 'X' or 'O'."""

    def __init__(self):
        self._board = [[None for _ in range(3)] for _ in range(3)]

    @property
    def board(self):
        return self._board

    def make_move(self, move, mark):
        row, column = move
        if self._board[row][column] is not None:
            raise ValueError("Cell already taken")
        self._board[row][column] = mark

    def undo_move(self, move):
        """Backtracking: restore the previous state."""
        row, column = move
        self._board[row][column] = None

    def get_available_moves(self):
        return [
            (r, c) for r in range(3) for c in range(3)
            if self._board[r][c] is None
        ]

    def _lines(self):
        b = self._board
        lines = [list(row) for row in b]
        lines += [[b[r][c] for r in range(3)] for c in range(3)]
        lines.append([b[i][i] for i in range(3)])
        lines.append([b[i][2 - i] for i in range(3)])
        return lines

    def get_winner(self):
        for line in self._lines():
            if line[0] is not None and line[0] == line[1] == line[2]:
                return line[0]
        return None

    def check_winner(self, mark):
        return self.get_winner() == mark

    def is_full(self):
        return not self.get_available_moves()

    def is_game_over(self):
        return self.get_winner() is not None or self.is_full()

    def to_features(self):
        """9 numeric features for ML: X=1, O=-1, empty=0."""
        code = {"X": 1, "O": -1, None: 0}
        return [code[cell] for row in self._board for cell in row]

    @classmethod
    def from_string(cls, text):
        """Build a model from the DB board string ('-' = empty)."""
        model = cls()
        for index, char in enumerate(text.strip()):
            if char in ("X", "O"):
                model._board[index // 3][index % 3] = char
        return model

    def to_string(self):
        return "".join(cell or "-" for row in self._board for cell in row)