"""
Module: minimax_agent.py
Subject: INF310 - Data Structures II
Description: Minimax agent for Tic-Tac-Toe using Backtracking
             (make_move / undo_move on the GameModel). Counts the
             visited nodes for educational purposes.
"""

from datastructures.game.game_model import GameModel


class MinimaxAgent:
    """Picks the optimal move by exploring the implicit game tree."""

    def __init__(self, ai_player="O", human_player="X"):
        self.ai_player = ai_player
        self.human_player = human_player
        self.nodes_evaluated = 0

    def evaluate(self, model):
        """Terminal score: +10 AI wins, -10 human wins, 0 otherwise."""
        if model.check_winner(self.ai_player):
            return 10
        if model.check_winner(self.human_player):
            return -10
        return 0

    def minimax(self, model, depth, is_maximizing):
        self.nodes_evaluated += 1
        score = self.evaluate(model)

        # Base cases (leaf nodes). Depth makes faster wins score higher.
        if score == 10:
            return score - depth
        if score == -10:
            return score + depth
        if model.is_full():
            return 0

        if is_maximizing:
            best_score = -float("inf")
            for move in model.get_available_moves():
                model.make_move(move, self.ai_player)
                best_score = max(
                    best_score, self.minimax(model, depth + 1, False)
                )
                model.undo_move(move)  # BACKTRACKING
            return best_score

        best_score = float("inf")
        for move in model.get_available_moves():
            model.make_move(move, self.human_player)
            best_score = min(
                best_score, self.minimax(model, depth + 1, True)
            )
            model.undo_move(move)  # BACKTRACKING
        return best_score

    def get_best_move(self, model):
        """Return the (row, column) with the best score for the AI,
        or None if the game is over. Resets the node counter."""
        self.nodes_evaluated = 0
        best_move = None
        best_score = -float("inf")

        for move in model.get_available_moves():
            model.make_move(move, self.ai_player)
            score = self.minimax(model, 1, False)
            model.undo_move(move)  # BACKTRACKING

            if score > best_score:
                best_score = score
                best_move = move
        return best_move