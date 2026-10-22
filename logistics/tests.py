import json
from django.test import TestCase
from unittest.mock import Mock, patch

import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from datastructures.game.game_model import GameModel
from datastructures.game.ml_agent import FEATURES, MLAgent
from logistics.services import game_service


class MLAgentExplanationTests(TestCase):
    def setUp(self):
        features = [[0] * 9, [0] * 9, [0] * 9]
        features[1][0] = 1
        features[2][0] = -1
        labels = [4, 5, 6]
        self.tree = DecisionTreeClassifier(random_state=42)
        self.tree.fit(pd.DataFrame(features, columns=FEATURES), labels)
        self.agent = MLAgent.__new__(MLAgent)
        self.agent.tree = self.tree
        self.agent.accuracy = 1.0

    def test_move_explanation_contains_the_actual_decision_path(self):
        model = GameModel()
        model.make_move((0, 0), "X")

        move, explanation = self.agent.get_move_with_explanation(model)

        self.assertEqual(move, (1, 2))
        self.assertEqual(explanation["predicted_cell"], 6)
        self.assertEqual(explanation["selected_cell"], 6)
        self.assertFalse(explanation["fallback_used"])
        self.assertEqual(explanation["accuracy"], 1.0)
        self.assertTrue(explanation["path"])
        self.assertEqual(explanation["path"][0]["cell"], 1)
        self.assertEqual(explanation["path"][0]["value"], 1)
        json.dumps(explanation)

    def test_move_explanation_reports_fallback_for_an_occupied_prediction(self):
        self.tree.fit(
            pd.DataFrame([[0] * 9, [1] + [0] * 8], columns=FEATURES),
            [0, 0],
        )
        model = GameModel()
        model.make_move((0, 0), "X")

        move, explanation = self.agent.get_move_with_explanation(model)

        self.assertEqual(move, (0, 1))
        self.assertEqual(explanation["predicted_cell"], 1)
        self.assertEqual(explanation["selected_cell"], 2)
        self.assertTrue(explanation["fallback_used"])


class GameServiceMLExplanationTests(TestCase):
    def test_ml_explanation_is_included_in_move_response(self):
        explanation = {
            "selected_cell": 2,
            "predicted_cell": 2,
            "fallback_used": False,
            "accuracy": 0.9,
            "path": [],
        }
        initial_game = {
            "id": 12,
            "board": "---------",
            "turn": "X",
            "mode": "ml",
            "status": "playing",
        }
        updated_game = {
            **initial_game,
            "board": "XO-------",
            "turn": "X",
        }
        ml_agent = Mock()
        ml_agent.get_move_with_explanation.return_value = ((0, 1), explanation)

        with (
            patch.object(game_service, "sp_get_game", side_effect=[initial_game, updated_game]),
            patch.object(game_service, "sp_make_move", return_value=game_service.STATUS_OK),
            patch.object(game_service, "_get_ml_agent", return_value=ml_agent),
        ):
            result = game_service.play_move(12, 0, 0)

        self.assertEqual(result["ml_explanation"], explanation)
