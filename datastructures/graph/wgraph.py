"""
Module: wgraph.py
Subject: INF310 - Data Structures II
Description: WGraph, a weighted graph built on top of Graph. The
             adjacency lists (indices) are inherited; the weights live
             in a dict {(origin_index, destination_index): weight}.
             Undirected by default; directed=True gives a weighted
             digraph (A -> B and B -> A can have different weights).

Author: Vladimir
"""

from datastructures.graph.graph import Graph
from datastructures.graph.data.adjacent_with_weight import AdjacentWithWeight
from datastructures.graph.data.edge import Edge


class WGraph(Graph):
    """Weighted graph: every edge carries a weight."""

    def __init__(self, vertices=None, directed=False):
        self._weights = {}
        super().__init__(vertices=vertices, directed=directed)

    # ------------------------------------------------------------------
    # Properties (Pythonic getters and setters)
    # ------------------------------------------------------------------
    @property
    def adjacency_matrix(self):
        """0/1 matrix (read-only here: use weight_matrix to set edges)."""
        return Graph.adjacency_matrix.fget(self)

    @property
    def adjacency_list(self):
        """Adjacency list (read-only here: use weight_matrix to set edges)."""
        return Graph.adjacency_list.fget(self)

    @property
    def weight_matrix(self):
        """Matrix of weights; None where there is no edge."""
        size = len(self._vertex_list)
        matrix = [[None] * size for _ in range(size)]
        for (origin, destination), weight in self._weights.items():
            matrix[origin][destination] = weight
        return matrix

    @weight_matrix.setter
    def weight_matrix(self, matrix):
        """Replace every edge from a matrix of weights (None = no edge).
        Must be square, match the vertices, and be symmetric if the
        graph is undirected."""
        size = len(self._vertex_list)
        if len(matrix) != size or any(len(row) != size for row in matrix):
            raise ValueError("Matrix must be square and match the vertices")
        if not self._directed:
            for i in range(size):
                for j in range(i):
                    if matrix[i][j] != matrix[j][i]:
                        raise ValueError("Undirected graph needs a symmetric matrix")
        self._adjacency_lists = [
            [j for j, weight in enumerate(row) if weight is not None]
            for row in matrix
        ]
        self._weights = {
            (i, j): weight
            for i, row in enumerate(matrix)
            for j, weight in enumerate(row)
            if weight is not None
        }

    @property
    def edges(self):
        """List of Edge(u, v, w) with vertex indices. In an undirected
        graph each edge appears once (u <= v)."""
        result = []
        for origin, adjacent in enumerate(self._adjacency_lists):
            for destination in adjacent:
                if self._directed or origin <= destination:
                    weight = self._weights[(origin, destination)]
                    result.append(Edge(origin, destination, weight))
        return result

    @classmethod
    def from_matrix(cls, vertices, matrix, directed=False):
        raise NotImplementedError("Use from_weight_matrix in a WGraph")

    @classmethod
    def from_weight_matrix(cls, vertices, matrix, directed=False):
        graph = cls(vertices, directed)
        graph.weight_matrix = matrix
        return graph

    # ------------------------------------------------------------------
    # Vertex methods
    # ------------------------------------------------------------------
    def delete_vertex(self, vertex):
        self._validate_vertex(vertex)
        deleted = self._get_num_of_vertex(vertex)
        shifted = {}
        for (origin, destination), weight in self._weights.items():
            if origin == deleted or destination == deleted:
                continue
            new_origin = origin - 1 if origin > deleted else origin
            new_destination = destination - 1 if destination > deleted else destination
            shifted[(new_origin, new_destination)] = weight
        super().delete_vertex(vertex)
        self._weights = shifted

    def adjacent_with_weight(self, vertex):
        """List of AdjacentWithWeight(index_of_vertex, weight)."""
        self._validate_vertex(vertex)
        origin = self._get_num_of_vertex(vertex)
        return [
            AdjacentWithWeight(destination, self._weights[(origin, destination)])
            for destination in self._adjacency_lists[origin]
        ]

    # ------------------------------------------------------------------
    # Edge methods
    # ------------------------------------------------------------------
    def insert_edge(self, origin_vertex, destination_vertex, weight):
        if weight is None:
            raise ValueError("Weight can't be None")
        super().insert_edge(origin_vertex, destination_vertex)
        origin = self._get_num_of_vertex(origin_vertex)
        destination = self._get_num_of_vertex(destination_vertex)
        self._weights[(origin, destination)] = weight
        if not self._directed:
            self._weights[(destination, origin)] = weight

    def delete_edge(self, origin_vertex, destination_vertex):
        super().delete_edge(origin_vertex, destination_vertex)
        origin = self._get_num_of_vertex(origin_vertex)
        destination = self._get_num_of_vertex(destination_vertex)
        self._weights.pop((origin, destination), None)
        if not self._directed:
            self._weights.pop((destination, origin), None)

    def get_edge_weight(self, origin_vertex, destination_vertex):
        if not self.exist_adjacency(origin_vertex, destination_vertex):
            raise ValueError("Edge not found")
        origin = self._get_num_of_vertex(origin_vertex)
        destination = self._get_num_of_vertex(destination_vertex)
        return self._weights[(origin, destination)]

    def set_edge_weight(self, origin_vertex, destination_vertex, weight):
        if weight is None:
            raise ValueError("Weight can't be None")
        if not self.exist_adjacency(origin_vertex, destination_vertex):
            raise ValueError("Edge not found")
        origin = self._get_num_of_vertex(origin_vertex)
        destination = self._get_num_of_vertex(destination_vertex)
        self._weights[(origin, destination)] = weight
        if not self._directed:
            self._weights[(destination, origin)] = weight