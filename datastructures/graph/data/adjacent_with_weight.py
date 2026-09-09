"""
Module: adjacent_with_weight.py
Subject: INF310 - Data Structures II
Description: AdjacentWithWeight, used inside WGraph's adjacency lists
             to hold a neighbor's vertex index plus the edge weight.
             Mirrors the Java AdjacentWithWeight class.

Author: Vladimir
"""


class AdjacentWithWeight:
    """Represents a weighted adjacency: (index_of_vertex, weight)."""

    def __init__(self, vertex, weight=0.0):
        self._index_of_vertex = vertex
        self._weight = weight

    # ------------------------------------------------------------------
    # Properties (Pythonic getters and setters)
    # ------------------------------------------------------------------
    @property
    def index_of_vertex(self):
        return self._index_of_vertex

    @index_of_vertex.setter
    def index_of_vertex(self, vertex):
        self._index_of_vertex = vertex

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, weight):
        self._weight = weight

    # ------------------------------------------------------------------
    # Comparable / equality (mirrors Java's compareTo/equals/hashCode)
    # ------------------------------------------------------------------
    def __lt__(self, other):
        # NOTE: ordered by index_of_vertex, same as the Java compareTo.
        # WGraph.prim_mst() relies on this exact ordering (see notes below).
        return self._index_of_vertex < other.index_of_vertex

    def __eq__(self, other):
        if other is None or not isinstance(other, AdjacentWithWeight):
            return False
        return self._index_of_vertex == other.index_of_vertex

    def __hash__(self):
        return hash(self._index_of_vertex)