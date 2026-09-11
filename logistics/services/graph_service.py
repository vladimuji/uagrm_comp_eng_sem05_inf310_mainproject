import json
from pathlib import Path
from datastructures.data.city_node import CityNode
from datastructures.data.route_edge import RouteEdge
from datastructures.graph.graph import Graph
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
