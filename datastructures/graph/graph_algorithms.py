"""
Module: graph_algorithms.py
Subject: INF310 - Data Structures II
Description: GraphAlgorithms, a toolbox of traversal (BFS/DFS),
             shortest-path (Dijkstra, Bellman-Ford) and MST (Prim,
             Kruskal) algorithms that operate on Graph/WGraph
             instances. Mirrors the Java GraphAlgorithms class.

Author: Vladimir
"""

import heapq
import itertools
from collections import deque

from datastructures.graph.data.edge import Edge
from datastructures.graph.data.union_find import UnionFind


class GraphAlgorithms:
    """Graph algorithms decoupled from the Graph/WGraph classes themselves."""

    # ------------------------------------------------------------------
    # Traversals
    # ------------------------------------------------------------------
    def breadth_first_search(self, graph, start):
        iteration = []
        visited = set()
        queue = deque([start])
        visited.add(start)

        while queue:
            node = queue.popleft()
            iteration.append(node)

            for n in graph.adjacent_of_vertex(node):
                if n not in visited:
                    queue.append(n)
                    visited.add(n)
        return iteration

    def depth_first_search(self, graph, start):
        iteration = []
        visited = set()
        self._dfs_recursive(graph, start, visited, iteration)
        return iteration

    def _dfs_recursive(self, graph, node, visited, iteration):
        visited.add(node)
        iteration.append(node)

        for n in graph.adjacent_of_vertex(node):
            if n not in visited:
                self._dfs_recursive(graph, n, visited, iteration)

    # ------------------------------------------------------------------
    # Shortest paths
    # ------------------------------------------------------------------
    def dijkstra(self, graph, source):
        # `vertices` returns a copy, so grab it once outside the loops.
        vertices = graph.vertices
        distance = {}
        visited = set()
        pq = []
        # A counter breaks ties without ever comparing two vertex
        # objects directly (Java's PriorityQueue.comparingByValue()
        # only ever compares the Double distance, never the key).
        counter = itertools.count()

        for vertex in vertices:
            distance[vertex] = float("inf")
        distance[source] = 0.0
        heapq.heappush(pq, (0.0, next(counter), source))

        while pq:
            current_distance, _, current = heapq.heappop(pq)
            if current in visited:
                continue
            visited.add(current)

            for adj in graph.adjacent_with_weight(current):
                neighbor = vertices[adj.index_of_vertex]
                new_dist = distance[current] + adj.weight
                if new_dist < distance[neighbor]:
                    distance[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, next(counter), neighbor))
        return distance

    def bellman_ford(self, graph, source):
        vertices = graph.vertices
        distance = {}
        for vertex in vertices:
            distance[vertex] = float("inf")
        distance[source] = 0.0

        v_count = len(vertices)
        edges = graph.edges

        # In an undirected WGraph each edge appears once (u <= v), so
        # relax it in both directions.
        if not graph.is_directed:
            edges = edges + [Edge(e.v, e.u, e.w) for e in edges if e.u != e.v]

        # Relax all edges V-1 times
        for _ in range(1, v_count):
            for edge in edges:
                u = vertices[edge.u]
                v = vertices[edge.v]

                if distance[u] != float("inf") and distance[u] + edge.w < distance[v]:
                    distance[v] = distance[u] + edge.w

        # Check for negative-weight cycles
        for edge in edges:
            u = vertices[edge.u]
            v = vertices[edge.v]

            if distance[u] != float("inf") and distance[u] + edge.w < distance[v]:
                raise RuntimeError("Graph contains a negative weight cycle")

        return distance

    # ------------------------------------------------------------------
    # Minimum spanning trees
    # ------------------------------------------------------------------
    def prim(self, graph, start):
        vertices = graph.vertices
        mst = []
        visited = set()
        pq = []

        start_index = vertices.index(start)
        visited.add(start)

        # Add all edges from the starting vertex
        for adj in graph.adjacent_with_weight(start):
            heapq.heappush(pq, Edge(start_index, adj.index_of_vertex, adj.weight))

        while pq and len(visited) < len(vertices):
            edge = heapq.heappop(pq)
            v = vertices[edge.v]

            if v in visited:
                continue

            mst.append(edge)
            visited.add(v)

            # Add new edges from the vertex just visited
            for adj in graph.adjacent_with_weight(v):
                if vertices[adj.index_of_vertex] not in visited:
                    heapq.heappush(pq, Edge(edge.v, adj.index_of_vertex, adj.weight))
        return mst

    def kruskal(self, graph):
        mst = []
        edges = graph.edges  # fresh list, safe to sort in place

        edges.sort()

        uf = UnionFind(graph.order())

        for edge in edges:
            if uf.find(edge.u) != uf.find(edge.v):
                uf.union(edge.u, edge.v)
                mst.append(edge)
        return mst