"""
Module: edge.py
Subject: INF310 - Data Structures II
Description: Edge, a simple (u, v, w) weighted edge used by Kruskal,
             Prim and Bellman-Ford. Mirrors the Java Edge class
             (public fields, no getters/setters -- same as Java).

Author: Vladimir
"""


class Edge:
    """Weighted edge between vertex indices u and v."""

    def __init__(self, u, v, w):
        self.u = u
        self.v = v
        self.w = w

    def __lt__(self, other):
        return self.w < other.w