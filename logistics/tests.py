import json
from decimal import Decimal
from datetime import datetime
from django.test import TestCase
from unittest.mock import Mock, patch
from django.db import ProgrammingError

import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from datastructures.game.game_model import GameModel
from datastructures.game.ml_agent import FEATURES, MLAgent
from datastructures.graph.digraph import DiGraph
from datastructures.graph.graph import Graph
from datastructures.heap.max_heap import MaxHeap
from datastructures.heap.min_heap import MinHeap
from logistics.services import game_service, graph_service
from logistics.services import dashboard_service
from logistics.services import cargo_services_service
from logistics.services import sql_result_service
from logistics.services import payments_service
from datastructures.graph.graph_algorithms import GraphAlgorithms
from datastructures.graph.wgraph import WGraph
from datastructures.graph.graph_adj_matrix import GraphAdjMatrix


class GraphRepresentationTests(TestCase):
    def test_graph_exposes_independent_adjacency_list_and_matrix_copies(self):
        graph = Graph(["A", "B", "C"])
        graph.insert_edge("A", "B")

        adjacency_list = graph.adjacency_list
        adjacency_matrix = graph.adjacency_matrix
        adjacency_list[0].clear()
        adjacency_matrix[0][1] = 0

        self.assertEqual(graph.adjacency_list, [["B"], ["A"], []])
        self.assertEqual(graph.adjacency_matrix, [
            [0, 1, 0],
            [1, 0, 0],
            [0, 0, 0],
        ])

    def test_set_vertex_preserves_edges_and_rejects_duplicate_values(self):
        graph = Graph(["A", "B"])
        graph.insert_edge("A", "B")

        graph.set_vertex("A", "X")

        self.assertEqual(graph.vertices, ["X", "B"])
        self.assertEqual(graph.adjacent_of_vertex("X"), ["B"])
        with self.assertRaises(ValueError):
            graph.set_vertex("X", "B")

    def test_digraph_keeps_direction_in_both_representations(self):
        graph = DiGraph(["A", "B", "C"])
        graph.insert_edge("A", "B")
        graph.insert_edge("A", "C")

        self.assertEqual(graph.adjacency_list, [["B", "C"], [], []])
        self.assertEqual(graph.adjacency_matrix, [
            [0, 1, 1],
            [0, 0, 0],
            [0, 0, 0],
        ])
        self.assertEqual(graph.size(), 2)
        self.assertFalse(graph.has_cycle())

        graph.insert_edge("B", "A")
        self.assertTrue(graph.has_cycle())

    def test_adjacency_list_setter_replaces_edges(self):
        graph = DiGraph(["A", "B", "C"])
        graph.adjacency_list = [["B", "C"], [], ["A"]]

        self.assertEqual(graph.adjacency_list, [["B", "C"], [], ["A"]])
        self.assertEqual(graph.adjacency_matrix, [
            [0, 1, 1],
            [0, 0, 0],
            [1, 0, 0],
        ])
        with self.assertRaises(ValueError):
            graph.adjacency_list = [["Z"], [], []]

        undirected = Graph(["A", "B"])
        with self.assertRaises(ValueError):
            undirected.adjacency_list = [["B"], []]  # not symmetric


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


class GraphAlgorithmsTests(TestCase):
    def setUp(self):
        self.algo = GraphAlgorithms()
        # Undirected: A-B 1, B-C 2, A-C 4, C-D 1
        self.undirected = WGraph(["A", "B", "C", "D"])
        self.undirected.insert_edge("A", "B", 1)
        self.undirected.insert_edge("B", "C", 2)
        self.undirected.insert_edge("A", "C", 4)
        self.undirected.insert_edge("C", "D", 1)

    def test_bfs_and_dfs_order(self):
        graph = Graph(["A", "B", "C", "D"])
        graph.insert_edge("A", "B")
        graph.insert_edge("A", "C")
        graph.insert_edge("B", "D")

        self.assertEqual(self.algo.breadth_first_search(graph, "A"), ["A", "B", "C", "D"])
        self.assertEqual(self.algo.depth_first_search(graph, "A"), ["A", "B", "D", "C"])

    def test_dijkstra_shortest_distances(self):
        distance = self.algo.dijkstra(self.undirected, "A")

        self.assertEqual(distance, {"A": 0.0, "B": 1, "C": 3, "D": 4})

    def test_bellman_ford_matches_dijkstra_on_undirected_graph(self):
        distance = self.algo.bellman_ford(self.undirected, "A")

        self.assertEqual(distance, {"A": 0.0, "B": 1, "C": 3, "D": 4})

    def test_bellman_ford_handles_negative_edges_in_directed_graph(self):
        graph = WGraph(["A", "B", "C", "D"], directed=True)
        graph.insert_edge("A", "B", 4)
        graph.insert_edge("A", "C", 2)
        graph.insert_edge("C", "B", -1)
        graph.insert_edge("B", "D", 1)

        distance = self.algo.bellman_ford(graph, "A")

        self.assertEqual(distance, {"A": 0.0, "B": 1, "C": 2, "D": 2})

    def test_bellman_ford_detects_negative_cycle(self):
        graph = WGraph(["A", "B", "C"], directed=True)
        graph.insert_edge("A", "B", 1)
        graph.insert_edge("B", "C", -2)
        graph.insert_edge("C", "A", -1)

        with self.assertRaises(RuntimeError):
            self.algo.bellman_ford(graph, "A")

    def test_prim_builds_minimum_spanning_tree(self):
        mst = self.algo.prim(self.undirected, "A")

        self.assertEqual(len(mst), 3)
        self.assertEqual(sum(edge.w for edge in mst), 4)

    def test_kruskal_builds_minimum_spanning_tree(self):
        mst = self.algo.kruskal(self.undirected)

        self.assertEqual(len(mst), 3)
        self.assertEqual(sum(edge.w for edge in mst), 4)


class GraphAdjMatrixTests(TestCase):
    def test_matrix_and_list_reflect_inserted_edges(self):
        graph = GraphAdjMatrix(["A", "B", "C"])
        graph.insert_edge("A", "B")

        self.assertEqual(graph.adjacency_matrix, [
            [0, 1, 0],
            [1, 0, 0],
            [0, 0, 0],
        ])
        self.assertEqual(graph.adjacency_list, [["B"], ["A"], []])
        self.assertEqual(graph.order(), 3)
        self.assertEqual(graph.size(), 1)

    def test_matrix_getter_returns_independent_copy(self):
        graph = GraphAdjMatrix(["A", "B"])
        graph.insert_edge("A", "B")

        matrix = graph.adjacency_matrix
        matrix[0][1] = 0

        self.assertEqual(graph.adjacency_matrix, [[0, 1], [1, 0]])

    def test_matrix_setter_validates_input(self):
        graph = GraphAdjMatrix(["A", "B"])

        graph.adjacency_matrix = [[0, 1], [1, 0]]
        self.assertEqual(graph.size(), 1)

        with self.assertRaises(ValueError):
            graph.adjacency_matrix = [[0, 1], [0, 0]]  # not symmetric
        with self.assertRaises(ValueError):
            graph.adjacency_matrix = [[0, 2], [2, 0]]  # values not 0/1
        with self.assertRaises(ValueError):
            graph.adjacency_matrix = [[0, 1, 0], [1, 0, 0]]  # wrong shape

    def test_adjacency_list_setter_replaces_edges(self):
        graph = GraphAdjMatrix(["A", "B", "C"], directed=True)
        graph.adjacency_list = [["B", "C"], [], ["A"]]

        self.assertEqual(graph.adjacency_list, [["B", "C"], [], ["A"]])
        self.assertEqual(graph.adjacency_matrix, [
            [0, 1, 1],
            [0, 0, 0],
            [1, 0, 0],
        ])
        with self.assertRaises(ValueError):
            graph.adjacency_list = [["Z"], [], []]  # unknown vertex
        with self.assertRaises(ValueError):
            graph.adjacency_list = [["B", "B"], [], []]  # duplicate neighbor

        undirected = GraphAdjMatrix(["A", "B"])
        with self.assertRaises(ValueError):
            undirected.adjacency_list = [["B"], []]  # not symmetric

    def test_delete_vertex_removes_row_and_column(self):
        graph = GraphAdjMatrix(["A", "B", "C"])
        graph.insert_edge("A", "B")
        graph.insert_edge("B", "C")

        graph.delete_vertex("B")

        self.assertEqual(graph.vertices, ["A", "C"])
        self.assertEqual(graph.adjacency_matrix, [[0, 0], [0, 0]])

    def test_traversals_cycles_and_islands(self):
        graph = GraphAdjMatrix(["A", "B", "C", "D"])
        graph.insert_edge("A", "B")
        graph.insert_edge("A", "C")
        graph.insert_edge("B", "D")

        self.assertEqual(graph.bfs("A"), ["A", "B", "C", "D"])
        self.assertEqual(graph.dfs_rec("A"), ["A", "B", "D", "C"])
        self.assertEqual(graph.dfs_iter("A"), ["A", "B", "D", "C"])
        self.assertFalse(graph.has_cycle())
        self.assertEqual(graph.count_islands(), 1)

        graph.insert_edge("C", "D")
        self.assertTrue(graph.has_cycle())


class GraphDemoApiTests(TestCase):
    def post(self, kind, payload):
        return self.client.post(
            f"/api/graphs/{kind}/", json.dumps(payload),
            content_type="application/json",
        )

    def test_default_graph_has_matrix_and_list(self):
        data = self.client.get("/api/graphs/graph/").json()
        self.assertEqual(data["order"], 5)
        self.assertEqual(data["size"], 5)
        self.assertEqual(data["adjacency_list"][0], ["B", "C"])

    def test_matrix_and_list_setters_through_api(self):
        response = self.post("digraph", {
            "vertices": ["A", "B"], "matrix": [[0, 1], [0, 0]]})
        self.assertEqual(response.json()["adjacency_list"], [["B"], []])

        response = self.post("digraph", {
            "vertices": ["A", "B"], "adjacency_list": [[], ["A"]]})
        self.assertEqual(response.json()["adjacency_matrix"], [[0, 0], [1, 0]])

    def test_setter_errors_return_400(self):
        response = self.post("graph", {
            "vertices": ["A", "B"], "matrix": [[0, 1], [0, 0]]})
        self.assertEqual(response.status_code, 400)  # not symmetric
        self.assertEqual(self.client.get("/api/graphs/nope/").status_code, 404)


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


class DashboardResultSetTests(TestCase):
    def test_result_set_reader_maps_each_result_set_by_column_name(self):
        cursor = Mock()
        cursor.description = [("first_value",)]
        cursor.fetchall.side_effect = [[(1,)], [(2,)]]

        second_result_set = False

        def advance_result_set():
            nonlocal second_result_set
            if second_result_set:
                return False
            second_result_set = True
            cursor.description = [("second_value",)]
            return True

        cursor.nextset.side_effect = advance_result_set

        result_sets = dashboard_service._read_result_sets(cursor)

        self.assertEqual(
            result_sets,
            [[{"first_value": 1}], [{"second_value": 2}]],
        )

    def test_revenue_months_are_passed_as_sql_parameters(self):
        cursor = Mock()
        cursor.__enter__ = Mock(return_value=cursor)
        cursor.__exit__ = Mock(return_value=False)
        cursor.description = [("mes",), ("anio",), ("total_ingresos",)]
        cursor.fetchall.return_value = [(11, 2026, 1250)]
        cursor.nextset.return_value = False

        with patch.object(
            sql_result_service.connection,
            "cursor",
            return_value=cursor,
        ):
            result = dashboard_service.get_revenue_by_month(3)

        cursor.execute.assert_called_once_with(
            "EXEC dbo.sp_dashboard_get_revenue_by_month @months=%s",
            [3],
        )
        self.assertEqual(
            result,
            [{"mes": 11, "anio": 2026, "total_ingresos": 1250}],
        )

    def test_recent_services_rejects_non_positive_limit(self):
        with self.assertRaises(ValueError):
            dashboard_service.get_recent_services(0)


class DashboardApiTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.create_user(
            username="dashboard-test",
            password="test-password",
        )
        self.client.force_login(user)

    def test_dashboard_api_requires_authentication(self):
        self.client.logout()

        response = self.client.get("/api/dashboard/kpis/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"error": "Authentication required"})

    @patch(
        "logistics.views.dashboard_api_views.dashboard_service."
        "get_fleet_availability"
    )
    def test_fleet_endpoint_returns_tabular_function_result(self, get_fleet):
        get_fleet.return_value = {
            "en_ruta": 4,
            "total": 10,
            "porcentaje": 40,
        }

        response = self.client.get("/api/dashboard/fleet-availability/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), get_fleet.return_value)

    @patch(
        "logistics.views.dashboard_api_views.dashboard_service."
        "get_recent_services"
    )
    def test_recent_services_endpoint_validates_limit(self, get_recent):
        response = self.client.get("/api/dashboard/recent-services/?top_n=0")

        self.assertEqual(response.status_code, 400)
        get_recent.assert_not_called()


class CargoServicesServiceTests(TestCase):
    @patch("logistics.services.cargo_services_service.execute_single_result_set")
    def test_list_filters_and_pagination_are_sql_parameters(self, execute):
        execute.return_value = [{"service_id": 41, "total_rows": 1}]

        result = cargo_services_service.list_cargo_services(
            customer_id=8,
            status_id=2,
            page_number=2,
            page_size=10,
        )

        self.assertEqual(
            execute.call_args.args[1],
            [None, None, 8, None, 2, 2, 10],
        )
        self.assertEqual(result["total_rows"], 1)
        self.assertEqual(result["results"], execute.return_value)

    @patch("logistics.services.cargo_services_service.execute_single_row")
    def test_status_count_function_receives_period_parameters(self, execute):
        execute.return_value = {"service_count": 4}

        result = cargo_services_service.get_services_count_by_status(
            status_id=3,
            month=11,
            year=2026,
        )

        self.assertEqual(execute.call_args.args[1], [3, 11, 2026])
        self.assertEqual(result, {"service_count": 4})

    def test_status_count_requires_month_and_year_together(self):
        with self.assertRaises(ValueError):
            cargo_services_service.get_services_count_by_status(3, month=11)


class CargoServicesApiTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.create_user(
            username="cargo-services-test",
            password="test-password",
        )
        self.client.force_login(user)

    @patch(
        "logistics.views.cargo_services_api_views."
        "cargo_services_service.create_cargo_service"
    )
    def test_create_requires_all_database_fields(self, create_service):
        response = self.client.post(
            "/api/operations/cargo-services/",
            data=json.dumps({"customer_id": 1}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        create_service.assert_not_called()

    @patch(
        "logistics.views.cargo_services_api_views."
        "cargo_services_service.create_cargo_service"
    )
    def test_create_returns_created_service_payload(self, create_service):
        create_service.return_value = {"service_id": 12, "status_id": 1}
        payload = {
            "customer_id": 3,
            "zone_id": 2,
            "cargo_type_id": 1,
            "cargo_detail": "Furniture move",
            "origin": "Origin address",
            "destination": "Destination address",
            "date_time_scheduled": "2026-12-01T10:00:00+02:00",
            "agreed_price": 350,
        }

        response = self.client.post(
            "/api/operations/cargo-services/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), create_service.return_value)
        self.assertEqual(
            create_service.call_args.kwargs["agreed_price"],
            Decimal("350"),
        )
        self.assertEqual(
            create_service.call_args.kwargs["date_time_scheduled"],
            datetime(2026, 12, 1, 8),
        )
        self.assertIsNone(create_service.call_args.kwargs["driver_id"])

    @patch(
        "logistics.views.cargo_services_api_views."
        "cargo_services_service.assign_cargo_service_driver"
    )
    def test_driver_assignment_is_an_update_not_resource_creation(
        self,
        assign_driver,
    ):
        assign_driver.return_value = {
            "service_id": 41,
            "driver_id": 7,
            "status_id": 2,
        }

        response = self.client.post(
            "/api/operations/cargo-services/41/assign-driver/",
            data=json.dumps({"driver_id": 7}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        assign_driver.assert_called_once_with(41, 7)

    @patch(
        "logistics.views.cargo_services_api_views."
        "cargo_services_service.get_cargo_service",
        side_effect=ProgrammingError(
            "42000",
            "[42000] [Microsoft][ODBC Driver 18 for SQL Server]"
            "[SQL Server]No se encontró el servicio solicitado. "
            "(51003) (SQLExecDirectW)",
        ),
    )
    def test_sql_not_found_error_becomes_http_404(self, get_service):
        response = self.client.get(
            "/api/operations/cargo-services/999999/"
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["code"], 51003)
        get_service.assert_called_once_with(999999)

    @patch(
        "logistics.views.cargo_services_api_views."
        "cargo_services_service.list_cargo_services"
    )
    def test_invalid_page_is_rejected_before_service_call(self, list_services):
        response = self.client.get(
            "/api/operations/cargo-services/?page=0"
        )

        self.assertEqual(response.status_code, 400)
        list_services.assert_not_called()


class PaymentsServiceTests(TestCase):
    @patch("logistics.services.payments_service.execute_single_result_set")
    def test_receipt_filters_are_bound_as_sql_parameters(self, execute):
        execute.return_value = [{"receipt_number": 12}]
        date_from = datetime(2026, 11, 1).date()
        date_to = datetime(2026, 11, 30).date()

        result = payments_service.list_payment_receipts(
            cargo_service_id=1022,
            payment_method=2,
            date_from=date_from,
            date_to=date_to,
        )

        self.assertEqual(
            execute.call_args.args[1],
            [1022, None, 2, date_from, date_to],
        )
        self.assertEqual(result, execute.return_value)

    @patch("logistics.services.payments_service.execute_single_row")
    def test_create_payment_is_parameterized_and_returns_receipt_number(
        self,
        execute,
    ):
        execute.return_value = {
            "receipt_number": 81,
            "remaining_balance": Decimal("12.50"),
        }

        result = payments_service.create_payment_receipt(
            cargo_service_id=1022,
            payment_method=2,
            amount="12.50",
            voucher_details="Bank transfer",
        )

        self.assertEqual(
            execute.call_args.args[1],
            [1022, 2, Decimal("12.50"), None, "Bank transfer"],
        )
        self.assertEqual(result["receipt_number"], 81)

    def test_create_payment_rejects_amount_outside_sql_decimal_shape(self):
        with self.assertRaises(ValueError):
            payments_service.create_payment_receipt(
                cargo_service_id=1022,
                payment_method=2,
                amount="1.001",
            )


class PaymentsApiTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.create_user(
            username="payments-test",
            password="test-password",
        )
        self.client.force_login(user)

    @patch(
        "logistics.views.payments_api_views."
        "payments_service.create_payment_receipt"
    )
    def test_create_payment_validates_amount_before_sql(self, create_payment):
        response = self.client.post(
            "/api/operations/payments/",
            data=json.dumps({
                "cargo_service_id": 1022,
                "payment_method": 2,
                "amount": "0",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        create_payment.assert_not_called()

    @patch(
        "logistics.views.payments_api_views."
        "payments_service.get_payment_receipt",
        side_effect=ProgrammingError(
            "42000",
            "[42000] [Microsoft][ODBC Driver 18 for SQL Server]"
            "[SQL Server]No se encontró el recibo solicitado. "
            "(51030) (SQLExecDirectW)",
        ),
    )
    def test_missing_receipt_maps_to_http_404(self, get_receipt):
        response = self.client.get("/api/operations/payments/2147483647/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["code"], 51030)
        get_receipt.assert_called_once_with(2147483647)

    @patch(
        "logistics.views.payments_api_views."
        "payments_service.list_payment_receipts"
    )
    def test_invalid_date_filter_is_rejected(self, list_receipts):
        response = self.client.get(
            "/api/operations/payments/?date_from=not-a-date"
        )

        self.assertEqual(response.status_code, 400)
        list_receipts.assert_not_called()