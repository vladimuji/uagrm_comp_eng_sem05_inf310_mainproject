"""
Module: ml_agent.py
Subject: INF310 - Data Structures II
Description: Builds a dataset from Minimax games and (next step)
             trains a DecisionTreeClassifier to imitate it.
"""

import random
import pandas as pd

from datastructures.game.game_model import GameModel
from datastructures.game.minimax_agent import MinimaxAgent
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

FEATURES = [f"c{i}" for i in range(9)]
COLUMNS = FEATURES + ["move"]


def generate_dataset(n_games=1000):
    """Minimax (O) vs random player (X).
    Each row = 9 features (X=1, O=-1, empty=0) + label (cell 0..8
    chosen by Minimax). Only positions where O has to move."""
    agent = MinimaxAgent("O", "X")
    cache = {}  # board string -> best cell, avoids recomputing Minimax
    rows = []

    for _ in range(n_games):
        model = GameModel()
        while not model.is_game_over():
            model.make_move(random.choice(model.get_available_moves()), "X")
            if model.is_game_over():
                break

            key = model.to_string()
            if key not in cache:
                move = agent.get_best_move(model)
                cache[key] = move[0] * 3 + move[1]
            cell = cache[key]

            rows.append(model.to_features() + [cell])
            model.make_move((cell // 3, cell % 3), "O")

    return rows

def build_dataframe(rows):
    """Rows -> DataFrame. Duplicated boards are removed so the test
    set does not contain positions already seen in training."""
    return pd.DataFrame(rows, columns=COLUMNS).drop_duplicates()


def train_model(df):
    """Returns (trained tree, accuracy on unseen positions)."""
    x_train, x_test, y_train, y_test = train_test_split(
        df[FEATURES], df["move"], test_size=0.2, random_state=42
    )
    tree = DecisionTreeClassifier(random_state=42)
    tree.fit(x_train, y_train)
    return tree, tree.score(x_test, y_test)


def show_rules(tree, max_depth=3):
    return export_text(tree, feature_names=FEATURES, max_depth=max_depth)