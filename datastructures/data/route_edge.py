# datastructures/data/route_edge.py

class RouteEdge:
    """Shared edge data used across graph/wgraph/graph_algorithms.
    Mirrors one row of the `edges` table."""

    def __init__(self, origin_node, destination_node, range_km,
                 locked_road, gas_cost, cash_cost, time_lapse,
                 google_json=None, weight_field="range_km"):
        self.origin_node = origin_node
        self.destination_node = destination_node
        self.range_km = range_km
        self.locked_road = locked_road
        self.gas_cost = gas_cost
        self.cash_cost = cash_cost
        self.time_lapse = time_lapse
        self.google_json = google_json or {}
        self._weight_field = weight_field  # which column drives comparisons

    @property
    def weight(self):
        return getattr(self, self._weight_field)

    # ---- Comparable-equivalent, used by Kruskal's edges.sort() ----
    def __lt__(self, other):
        return self.weight < other.weight

    def __gt__(self, other):
        return self.weight > other.weight

    def __eq__(self, other):
        if not isinstance(other, RouteEdge):
            return NotImplemented
        return (
            self.origin_node == other.origin_node
            and self.destination_node == other.destination_node
        )

    def __hash__(self):
        return hash((self.origin_node, self.destination_node))

    def to_dict(self):
        return {
            "origin_node": self.origin_node,
            "destination_node": self.destination_node,
            "range_km": self.range_km,
            "locked_road": self.locked_road,
            "gas_cost": self.gas_cost,
            "cash_cost": self.cash_cost,
            "time_lapse": str(self.time_lapse),
            "google_json": self.google_json,
        }

    def __str__(self):
        return f"{self.origin_node} -> {self.destination_node} ({self.weight})"

    def __repr__(self):
        return f"RouteEdge({self.origin_node!r}, {self.destination_node!r}, w={self.weight})"