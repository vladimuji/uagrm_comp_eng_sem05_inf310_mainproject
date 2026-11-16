import json
from django.test import TestCase
from unittest.mock import Mock, patch

import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from datastructures.game.game_model import GameModel
from datastructures.game.ml_agent import FEATURES, MLAgent
from datastructures.graph.digraph import DiGraph
from datastructures.graph.graph import Graph
from datastructures.heap.max_heap import MaxHeap
from datastructures.heap.min_heap import MinHeap
from logistics.services import game_service, graph_service


class GraphRepresentationTests(TestCase):
    def test_graph_exposes_independent_adjacency_list_and_matrix_copies(self):
        graph = Graph(["A", "B", "C"])
        graph.insert_edge("A", "B")

        adjacency_list = graph.get_adjacency_list()
        adjacency_matrix = graph.get_adjacency_matrix()
        adjacency_list[0].clear()
        adjacency_matrix[0][1] = 0

        self.assertEqual(graph.get_adjacency_list(), [["B"], ["A"], []])
        self.assertEqual(graph.get_adjacency_matrix(), [
            [0, 1, 0],
            [1, 0, 0],
            [0, 0, 0],
        ])

    def test_set_vertex_preserves_edges_and_rejects_duplicate_values(self):
        graph = Graph(["A", "B"])
        graph.insert_edge("A", "B")

        graph.set_vertex("A", "X")

        self.assertEqual(graph.get_vertices(), ["X", "B"])
        self.assertEqual(graph.adjacent_of_vertex("X"), ["B"])
        with self.assertRaises(ValueError):
            graph.set_vertex("X", "B")

    def test_digraph_keeps_direction_in_both_representations(self):
        graph = DiGraph(["A", "B", "C"])
        graph.insert_edge("A", "B")
        graph.insert_edge("A", "C")

        self.assertEqual(graph.get_adjacency_list(), [["B", "C"], [], []])
        self.assertEqual(graph.get_adjacency_matrix(), [
            [0, 1, 1],
            [0, 0, 0],
            [0, 0, 0],
        ])
        self.assertEqual(graph.number_of_edges(), 2)
        self.assertFalse(graph.has_cycle())

        graph.insert_edge("B", "A")
        self.assertTrue(graph.has_cycle())


class GraphRepresentationViewTests(TestCase):
    @patch("logistics.views.views.graph_service.get_graph_representation")
    def test_graph_page_renders_database_representations(self, get_graph_data):
        city_a = {"id": 1, "city_name": "City A", "state": "State"}
        city_b = {"id": 2, "city_name": "City B", "state": "State"}
        get_graph_data.return_value = {
            "nodes": [city_a, city_b],
            "edges": [{"origin": 1, "destination": 2}],
            "adjacency_list": [
                {"vertex": city_a, "neighbors": [city_b]},
                {"vertex": city_b, "neighbors": []},
            ],
            "matrix_rows": [
                {"vertex": city_a, "values": [0, 1]},
                {"vertex": city_b, "values": [0, 0]},
            ],
            "vertex_count": 2,
            "edge_count": 1,
        }

        response = self.client.get("/graphs/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adjacency list")
        self.assertContains(response, "Adjacency matrix")
        self.assertContains(response, "City A")
        self.assertContains(response, "City B")


class GraphServiceRepresentationTests(TestCase):
    def test_graph_representation_uses_listed_nodes_and_directed_routes(self):
        nodes = [
            {"id": 1, "city_name": "City A", "state": "State"},
            {"id": 2, "city_name": "City B", "state": "State"},
        ]
        routes = [{"origin_node_id": 1, "destination_node_id": 2}]
        node_query = Mock()
        node_query.order_by.return_value.values.return_value = nodes
        route_query = Mock()
        route_query.order_by.return_value.values.return_value = routes

        with (
            patch(
                "logistics.services.graph_service.Node.objects.filter",
                return_value=node_query,
            ),
            patch(
                "logistics.services.graph_service.Route.objects.filter",
                return_value=route_query,
            ),
        ):
            result = graph_service.get_graph_representation()

        self.assertEqual(result["vertex_count"], 2)
        self.assertEqual(result["edge_count"], 1)
        self.assertEqual(
            [row["values"] for row in result["matrix_rows"]],
            [[0, 1], [0, 0]],
        )
        self.assertEqual(
            result["adjacency_list"][0]["neighbors"],
            [nodes[1]],
        )


class HeapInterfaceTests(TestCase):
    def test_min_and_max_heaps_implement_the_restored_interface(self):
        min_heap = MinHeap()
        max_heap = MaxHeap()
        for value in (3, 1, 2):
            min_heap.insert(value)
            max_heap.insert(value)

        self.assertEqual(min_heap.extract_root(), 1)
        self.assertEqual(max_heap.extract_root(), 3)


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
