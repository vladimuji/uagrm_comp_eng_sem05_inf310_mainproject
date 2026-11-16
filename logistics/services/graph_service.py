import json
from pathlib import Path
from datastructures.data.city_node import CityNode
from datastructures.data.route_edge import RouteEdge
from datastructures.graph.digraph import DiGraph
from logistics.models import Node, Route


def get_graph_data():
	data_dir = Path(__file__).parent.parent / "data"

	with (data_dir / "nodes_copy.json").open(encoding="utf-8") as nodes_file:
		nodes = json.load(nodes_file)

	with (data_dir / "edges_copy.json").open(encoding="utf-8") as edges_file:
		edges = json.load(edges_file)

	return {"nodes": nodes, "edges": edges}


def build_route_edges(weight_field="range_km"):
    rows = Route.objects.values()
    return [
        RouteEdge(**row, weight_field=weight_field)
        for row in rows
    ]


def _extract_polyline(google_json):
    if isinstance(google_json, str):
        try:
            google_json = json.loads(google_json)
        except ValueError:
            return None
    return ((google_json or {}).get("directions") or {}).get("overview_polyline")


def get_map_data():
    nodes = list(Node.objects.order_by("id").values(
        "id", "city_name", "state", "latitude", "longitude", "listed"))
    edges = [
        {
            "origin": r["origin_node_id"],
            "destination": r["destination_node_id"],
            "range_km": r["range_km"],
            "locked": r["locked_road"],
            "gas_cost": r["gas_cost"],
            "cash_cost": r["cash_cost"],
            "time": str(r["time_lapse"]),
            "polyline": _extract_polyline(r["google_json"]),
        }
        for r in Route.objects.values(
            "origin_node_id", "destination_node_id", "range_km", "locked_road",
            "gas_cost", "cash_cost", "time_lapse", "google_json")
    ]
    pairs = {(e["origin"], e["destination"]) for e in edges}
    for e in edges:
        e["two_way"] = (e["destination"], e["origin"]) in pairs
    return {"nodes": nodes, "edges": edges}


def get_graph_representation():
    nodes = list(
        Node.objects.filter(listed=True)
        .order_by("id")
        .values("id", "city_name", "state")
    )
    node_ids = [node["id"] for node in nodes]
    graph = DiGraph(node_ids)

    edges = []
    if node_ids:
        edges = list(
            Route.objects.filter(
                origin_node_id__in=node_ids,
                destination_node_id__in=node_ids,
            )
            .order_by("origin_node_id", "destination_node_id")
            .values("origin_node_id", "destination_node_id")
        )
        for edge in edges:
            graph.insert_edge(
                edge["origin_node_id"],
                edge["destination_node_id"],
            )

    node_by_id = {node["id"]: node for node in nodes}
    adjacency_list = [
        {
            "vertex": node_by_id[node],
            "neighbors": [node_by_id[neighbor] for neighbor in adjacent],
        }
        for node, adjacent in zip(node_ids, graph.get_adjacency_list())
    ]
    matrix_rows = [
        {"vertex": node_by_id[node], "values": row}
        for node, row in zip(node_ids, graph.get_adjacency_matrix())
    ]

    return {
        "nodes": nodes,
        "edges": [
            {
                "origin": edge["origin_node_id"],
                "destination": edge["destination_node_id"],
            }
            for edge in edges
        ],
        "adjacency_list": adjacency_list,
        "matrix_rows": matrix_rows,
        "vertex_count": graph.number_of_vertices(),
        "edge_count": graph.number_of_edges(),
    }