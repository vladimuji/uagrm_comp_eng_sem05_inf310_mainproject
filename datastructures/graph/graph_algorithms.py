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

from graph.data.edge import Edge
from graph.data.union_find import UnionFind


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
        distance = {}
        visited = set()
        pq = []
        # A counter breaks ties without ever comparing two vertex
        # objects directly (Java's PriorityQueue.comparingByValue()
        # only ever compares the Double distance, never the key).
        counter = itertools.count()

        for vertex in graph._vertex_list:
            distance[vertex] = float("inf")
        distance[source] = 0.0
        heapq.heappush(pq, (0.0, next(counter), source))

        while pq:
            current_distance, _, current = heapq.heappop(pq)
            if current in visited:
                continue
            visited.add(current)

            for adj in graph.adjacent_of_vertex(current):
                neighbor_index = adj.index_of_vertex
                neighbor = graph._vertex_list[neighbor_index]
                weight = adj.weight

                new_dist = distance[current] + weight
                if new_dist < distance[neighbor]:
                    distance[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, next(counter), neighbor))
        return distance

    def bellman_ford(self, graph, source):
        distance = {}
        for vertex in graph._vertex_list:
            distance[vertex] = float("inf")
        distance[source] = 0.0

        v_count = len(graph._vertex_list)
        edges = graph.get_edges()  # this method was added on WGraph

        # Relax all edges V-1 times
        for _ in range(1, v_count):
            for edge in edges:
                u = graph._vertex_list[edge.u]
                v = graph._vertex_list[edge.v]

                if distance[u] != float("inf") and distance[u] + edge.w < distance[v]:
                    distance[v] = distance[u] + edge.w

        # Check for negative-weight cycles
        for edge in edges:
            u = graph._vertex_list[edge.u]
            v = graph._vertex_list[edge.v]

            if distance[u] != float("inf") and distance[u] + edge.w < distance[v]:
                raise RuntimeError("Graph contains a negative weight cycle")

        return distance

    # ------------------------------------------------------------------
    # Minimum spanning trees
    # ------------------------------------------------------------------
    def prim(self, graph, start):
        mst = []
        visited = set()
        pq = []

        start_index = graph._vertex_list.index(start)
        visited.add(start)

        # Add all edges from the starting vertex
        for adj in graph.adjacent_of_vertex(start):
            heapq.heappush(pq, Edge(start_index, adj.index_of_vertex, adj.weight))

        while pq and len(visited) < len(graph._vertex_list):
            edge = heapq.heappop(pq)
            v = graph._vertex_list[edge.v]

            if v in visited:
                continue

            mst.append(edge)
            visited.add(v)

            # Add new edges from the vertex just visited
            for adj in graph.adjacent_of_vertex(v):
                if graph._vertex_list[adj.index_of_vertex] not in visited:
                    heapq.heappush(pq, Edge(edge.v, adj.index_of_vertex, adj.weight))
        return mst

    def kruskal(self, graph):
        mst = []
        edges = graph.get_edges()

        edges.sort()

        uf = UnionFind(len(graph._vertex_list))

        for edge in edges:
            if uf.find(edge.u) != uf.find(edge.v):
                uf.union(edge.u, edge.v)
                mst.append(edge)
        return mst