import json
from pathlib import Path


def get_graph_data():
	data_dir = Path(__file__).parent.parent / "data"

	with (data_dir / "nodes_copy.json").open(encoding="utf-8") as nodes_file:
		nodes = json.load(nodes_file)

	with (data_dir / "edges_copy.json").open(encoding="utf-8") as edges_file:
		edges = json.load(edges_file)

	return {"nodes": nodes, "edges": edges}
