"""Directed graph implemented with adjacency lists."""

from datastructures.graph.graph import Graph


class DiGraph(Graph):
    """Directed graph whose edges point from origin to destination."""

    def __init__(self, vertices=None):
        super().__init__(vertices=vertices, directed=True)
