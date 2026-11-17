"""
Module: digraph.py
Subject: INF310 - Data Structures II
Description: DiGraph, a directed adjacency-list graph. Reuses Graph
             with directed=True: an edge A -> B does not imply B -> A.

Author: Vladimir
"""

from datastructures.graph.graph import Graph


class DiGraph(Graph):
    """Directed graph whose edges point from origin to destination."""

    def __init__(self, vertices=None):
        super().__init__(vertices=vertices, directed=True)

    @classmethod
    def from_matrix(cls, vertices, matrix):
        """Build a DiGraph from a 0/1 matrix (does not need to be
        symmetric: matrix[i][j] == 1 means edge i -> j)."""
        graph = cls(vertices)
        graph.adjacency_matrix = matrix
        return graph