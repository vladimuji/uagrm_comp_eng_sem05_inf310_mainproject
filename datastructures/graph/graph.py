"""
Module: graph.py
Subject: INF310 - Data Structures II
Description: Graph, a basic undirected graph using an adjacency-list
             representation (vertex_list + parallel adjacency_lists of
             indices). Mirrors the Java Graph class.

Author: Vladimir
"""

from collections import deque


class Graph:
    """Undirected graph over vertices of any comparable/hashable type."""

    INVALID_VERTEX_NUM = -1

    def __init__(self, vertices=None):
        self._vertex_list = []
        self._adjacency_lists = []
        if vertices is not None:
            for vertex in vertices:
                self.insert_vertex(vertex)

    # ------------------------------------------------------------------
    # Vertex methods
    # ------------------------------------------------------------------
    def insert_vertex(self, vertex):
        if self.exist_vertex(vertex):
            raise ValueError("Vertex already exists in the Graph")
        self._vertex_list.append(vertex)
        self._adjacency_lists.append([])

    def exist_vertex(self, vertex):
        if vertex is None:
            raise ValueError("Vertex can't be None")
        return self._get_num_of_vertex(vertex) != Graph.INVALID_VERTEX_NUM

    def delete_vertex(self, vertex):
        self._validate_vertex(vertex)
        num_vertex_to_delete = self._get_num_of_vertex(vertex)
        self._vertex_list.pop(num_vertex_to_delete)
        self._adjacency_lists.pop(num_vertex_to_delete)
        for adjacent_of_vertex in self._adjacency_lists:
            if num_vertex_to_delete in adjacent_of_vertex:
                adjacent_of_vertex.remove(num_vertex_to_delete)
            for i in range(len(adjacent_of_vertex)):
                adjacency = adjacent_of_vertex[i]
                if adjacency > num_vertex_to_delete:
                    adjacent_of_vertex[i] = adjacency - 1

    def exist_adjacency(self, origin_vertex, destination_vertex):
        self._validate_vertex(origin_vertex)
        self._validate_vertex(destination_vertex)
        num_origin_vertex = self._get_num_of_vertex(origin_vertex)
        num_destination_vertex = self._get_num_of_vertex(destination_vertex)
        adjacent_of_origin = self._adjacency_lists[num_origin_vertex]
        return num_destination_vertex in adjacent_of_origin

    def _validate_vertex(self, vertex):
        if vertex is None:
            raise ValueError("Vertex can't be None")
        if self._get_num_of_vertex(vertex) == Graph.INVALID_VERTEX_NUM:
            raise ValueError("Vertex not found")

    def _get_num_of_vertex(self, vertex):
        for i in range(len(self._vertex_list)):
            if self._vertex_list[i] == vertex:
                return i
        return Graph.INVALID_VERTEX_NUM

    def vertex_degree(self, vertex):
        self._validate_vertex(vertex)
        num_of_vertex = self._get_num_of_vertex(vertex)
        adjacent_of_vertex = self._adjacency_lists[num_of_vertex]
        return len(adjacent_of_vertex)

    def get_vertices(self):
        return list(self._vertex_list)

    def adjacent_of_vertex(self, vertex):
        self._validate_vertex(vertex)
        adjacent_vertices = []
        num_of_vertex = self._get_num_of_vertex(vertex)
        adjacent_of_vertex_list = self._adjacency_lists[num_of_vertex]
        for pos_adj in adjacent_of_vertex_list:
            adjacent_vertices.append(self._vertex_list[pos_adj])
        return adjacent_vertices

    def get_vertex_by_number(self, num_of_vertex):
        if num_of_vertex < 0 or num_of_vertex >= len(self._vertex_list):
            raise ValueError("Invalid number of Vertex")
        return self._vertex_list[num_of_vertex]

    def number_of_vertices(self):
        return len(self._vertex_list)

    # ------------------------------------------------------------------
    # Edge methods
    # ------------------------------------------------------------------
    def insert_edge(self, origin_vertex, destination_vertex):
        if self.exist_adjacency(origin_vertex, destination_vertex):
            raise ValueError("Edge already exists in the graph")
        num_origin_vertex = self._get_num_of_vertex(origin_vertex)
        num_destination_vertex = self._get_num_of_vertex(destination_vertex)
        adjacent_of_origin = self._adjacency_lists[num_origin_vertex]
        adjacent_of_origin.append(num_destination_vertex)
        adjacent_of_origin.sort()
        if num_origin_vertex != num_destination_vertex:
            adjacent_of_destination = self._adjacency_lists[num_destination_vertex]
            adjacent_of_destination.append(num_origin_vertex)
            adjacent_of_destination.sort()

    def delete_edge(self, origin_vertex, destination_vertex):
        self._validate_vertex(origin_vertex)
        self._validate_vertex(destination_vertex)
        num_origin_vertex = self._get_num_of_vertex(origin_vertex)
        num_destination_vertex = self._get_num_of_vertex(destination_vertex)
        adjacent_of_origin = self._adjacency_lists[num_origin_vertex]
        adjacent_of_destination = self._adjacency_lists[num_destination_vertex]
        if num_destination_vertex in adjacent_of_origin:
            adjacent_of_origin.remove(num_destination_vertex)
        if num_origin_vertex in adjacent_of_destination:
            adjacent_of_destination.remove(num_origin_vertex)

    def number_of_edges(self):
        count = 0
        for adjacency in self._adjacency_lists:
            count += len(adjacency)
        return count // 2

    # ------------------------------------------------------------------
    # Traversals
    # ------------------------------------------------------------------
    def dfs_rec(self, start_vertex):
        self._validate_vertex(start_vertex)
        visited = []
        marked = [False] * len(self._vertex_list)
        self._dfs_rec_helper(self._get_num_of_vertex(start_vertex), marked, visited)
        return visited

    def _dfs_rec_helper(self, vertex_num, marked, visited):
        marked[vertex_num] = True
        visited.append(self._vertex_list[vertex_num])
        for adj in self._adjacency_lists[vertex_num]:
            if not marked[adj]:
                self._dfs_rec_helper(adj, marked, visited)

    def dfs_iter(self, start_vertex):
        self._validate_vertex(start_vertex)
        visited = []
        marked = [False] * len(self._vertex_list)
        stack = [self._get_num_of_vertex(start_vertex)]
        while stack:
            vertex_num = stack.pop()
            if not marked[vertex_num]:
                marked[vertex_num] = True
                visited.append(self._vertex_list[vertex_num])
                # Keep a consistent order: push neighbors in reverse.
                adjacents = self._adjacency_lists[vertex_num]
                for i in range(len(adjacents) - 1, -1, -1):
                    adj = adjacents[i]
                    if not marked[adj]:
                        stack.append(adj)
        return visited

    def bfs(self, start_vertex):
        self._validate_vertex(start_vertex)
        return self._bfs_iter(start_vertex)

    def _bfs_iter(self, start_vertex):
        visited = []
        queue = deque()
        marked = [False] * len(self._vertex_list)
        start_num = self._get_num_of_vertex(start_vertex)
        queue.append(start_num)
        marked[start_num] = True
        while queue:
            vertex_num = queue.popleft()
            visited.append(self._vertex_list[vertex_num])
            for adj in self._adjacency_lists[vertex_num]:
                if not marked[adj]:
                    queue.append(adj)
                    marked[adj] = True
        return visited

    def has_cycle(self):
        visited = [False] * len(self._vertex_list)
        for i in range(len(self._vertex_list)):
            if not visited[i]:
                if self._dfs_cycle_undirected(i, -1, visited):
                    return True
        return False

    def _dfs_cycle_undirected(self, v, parent, visited):
        visited[v] = True
        for adj in self._adjacency_lists[v]:
            if not visited[adj]:
                if self._dfs_cycle_undirected(adj, v, visited):
                    return True
            elif adj != parent:
                return True  # visited neighbor that is not the parent -> real cycle
        return False

    def count_islands(self):
        visited = [False] * len(self._vertex_list)
        island_count = 0
        for i in range(len(self._vertex_list)):
            if not visited[i]:
                island_count += 1
                self._dfs_mark_island(i, visited)
        return island_count

    def _dfs_mark_island(self, v, visited):
        visited[v] = True
        for adj in self._adjacency_lists[v]:
            if not visited[adj]:
                self._dfs_mark_island(adj, visited)

    def is_reachable(self, origin, destination):
        if not self.exist_vertex(origin) or not self.exist_vertex(destination):
            raise ValueError("Vertex not found")
        if origin == destination:
            return True
        visited = {v: False for v in self.get_vertices()}
        queue = deque([origin])
        visited[origin] = True
        while queue:
            current = queue.popleft()
            for adj in self.adjacent_of_vertex(current):
                if adj == destination:
                    return True
                if not visited[adj]:
                    visited[adj] = True
                    queue.append(adj)
        return False