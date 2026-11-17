"""
Module: graph.py
Subject: INF310 - Data Structures II
Description: Graph, an adjacency-list graph (undirected by default),
             using vertex_list and parallel adjacency_lists of indices.

             Terminology (formal graph theory):
                 order() -> number of vertices
                 size()  -> number of edges

Author: Vladimir
"""

from collections import deque


class Graph:
    """Adjacency-list graph over vertices of any comparable/hashable type."""

    INVALID_VERTEX_NUM = -1

    def __init__(self, vertices=None, directed=False):
        self._vertex_list = []
        self._adjacency_lists = []
        self._directed = directed
        if vertices is not None:
            for vertex in vertices:
                self.insert_vertex(vertex)

    # ------------------------------------------------------------------
    # Properties (Pythonic getters and setters)
    # ------------------------------------------------------------------
    @property
    def is_directed(self):
        return self._directed

    @property
    def vertices(self):
        """Copy of the vertex list."""
        return list(self._vertex_list)

    @property
    def adjacency_list(self):
        """Copy of the adjacency list, expressed with the vertices."""
        return [
            [self._vertex_list[index] for index in adjacent]
            for adjacent in self._adjacency_lists
        ]
    
    @adjacency_list.setter
    def adjacency_list(self, adjacency_list):
        """Replace every edge from a list of neighbor lists (expressed
        with vertices). Must have one entry per vertex, no unknown or
        repeated neighbors, and be symmetric if the graph is undirected."""
        size = len(self._vertex_list)
        if len(adjacency_list) != size:
            raise ValueError("Adjacency list must have one entry per vertex")
        new_lists = []
        for neighbors in adjacency_list:
            indices = []
            for vertex in neighbors:
                num = self._get_num_of_vertex(vertex)
                if num == Graph.INVALID_VERTEX_NUM:
                    raise ValueError("Vertex not found")
                if num in indices:
                    raise ValueError("Duplicate neighbor in adjacency list")
                indices.append(num)
            new_lists.append(sorted(indices))
        if not self._directed:
            for i, row in enumerate(new_lists):
                for j in row:
                    if i not in new_lists[j]:
                        raise ValueError(
                            "Undirected graph needs a symmetric adjacency list"
                        )
        self._adjacency_lists = new_lists

    @property
    def adjacency_matrix(self):
        """Matrix built on the fly from the adjacency lists."""
        matrix = [
            [0] * len(self._vertex_list)
            for _ in self._vertex_list
        ]
        for origin, adjacent in enumerate(self._adjacency_lists):
            for destination in adjacent:
                matrix[origin][destination] = 1
        return matrix

    @adjacency_matrix.setter
    def adjacency_matrix(self, matrix):
        """Replace every edge from a 0/1 matrix. Must be square, match
        the vertices, and be symmetric if the graph is undirected."""
        size = len(self._vertex_list)
        if len(matrix) != size or any(len(row) != size for row in matrix):
            raise ValueError("Matrix must be square and match the vertices")
        if any(value not in (0, 1) for row in matrix for value in row):
            raise ValueError("Matrix values must be 0 or 1")
        if not self._directed:
            for i in range(size):
                for j in range(i):
                    if matrix[i][j] != matrix[j][i]:
                        raise ValueError("Undirected graph needs a symmetric matrix")
        self._adjacency_lists = [
            [j for j, value in enumerate(row) if value] for row in matrix
        ]

    @classmethod
    def from_matrix(cls, vertices, matrix, directed=False):
        graph = cls(vertices, directed)
        graph.adjacency_matrix = matrix
        return graph

    # ------------------------------------------------------------------
    # Graph info
    # ------------------------------------------------------------------
    def order(self):
        """Return the number of vertices."""
        return len(self._vertex_list)

    def size(self):
        """Return the number of edges."""
        count = 0
        self_loops = 0
        for vertex_num, adjacency in enumerate(self._adjacency_lists):
            count += len(adjacency)
            if vertex_num in adjacency:
                self_loops += 1
        if self._directed:
            return count
        return (count + self_loops) // 2

    def is_empty(self):
        """Return True if the graph has no vertices."""
        return len(self._vertex_list) == 0

    # ------------------------------------------------------------------
    # Vertex methods
    # ------------------------------------------------------------------
    def insert_vertex(self, vertex):
        if vertex is None:
            raise ValueError("Vertex can't be None")
        if self.exist_vertex(vertex):
            raise ValueError("Vertex already exists in the Graph")
        self._vertex_list.append(vertex)
        self._adjacency_lists.append([])

    def set_vertex(self, old_vertex, new_vertex):
        """Replace a vertex keeping its edges."""
        self._validate_vertex(old_vertex)
        if new_vertex is None:
            raise ValueError("Vertex can't be None")
        new_vertex_num = self._get_num_of_vertex(new_vertex)
        old_vertex_num = self._get_num_of_vertex(old_vertex)
        if new_vertex_num != Graph.INVALID_VERTEX_NUM and new_vertex_num != old_vertex_num:
            raise ValueError("Vertex already exists in the Graph")
        self._vertex_list[old_vertex_num] = new_vertex

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

    def vertex_degree(self, vertex):
        self._validate_vertex(vertex)
        num_of_vertex = self._get_num_of_vertex(vertex)
        adjacent_of_vertex = self._adjacency_lists[num_of_vertex]
        return len(adjacent_of_vertex)

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
        if not self._directed and num_origin_vertex != num_destination_vertex:
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
        if not self._directed and num_origin_vertex in adjacent_of_destination:
            adjacent_of_destination.remove(num_origin_vertex)

    def exist_adjacency(self, origin_vertex, destination_vertex):
        self._validate_vertex(origin_vertex)
        self._validate_vertex(destination_vertex)
        num_origin_vertex = self._get_num_of_vertex(origin_vertex)
        num_destination_vertex = self._get_num_of_vertex(destination_vertex)
        adjacent_of_origin = self._adjacency_lists[num_origin_vertex]
        return num_destination_vertex in adjacent_of_origin

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

    def is_reachable(self, origin, destination):
        self._validate_vertex(origin)
        self._validate_vertex(destination)
        return destination in self.bfs(origin)

    # ------------------------------------------------------------------
    # Cycles and components
    # ------------------------------------------------------------------
    def has_cycle(self):
        if self._directed:
            state = [0] * len(self._vertex_list)
            for vertex_num in range(len(self._vertex_list)):
                if state[vertex_num] == 0 and self._dfs_directed_cycle(vertex_num, state):
                    return True
            return False

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

    def _dfs_directed_cycle(self, vertex_num, state):
        state[vertex_num] = 1
        for adjacent in self._adjacency_lists[vertex_num]:
            if state[adjacent] == 1:
                return True
            if state[adjacent] == 0 and self._dfs_directed_cycle(adjacent, state):
                return True
        state[vertex_num] = 2
        return False

    def count_islands(self):
        visited = [False] * len(self._vertex_list)
        island_count = 0
        for i in range(len(self._vertex_list)):
            if not visited[i]:
                island_count += 1
                if self._directed:
                    self._dfs_mark_weak_component(i, visited)
                else:
                    self._dfs_mark_island(i, visited)
        return island_count

    def _dfs_mark_weak_component(self, vertex_num, visited):
        visited[vertex_num] = True
        neighbors = set(self._adjacency_lists[vertex_num])
        neighbors.update(
            origin for origin, adjacent in enumerate(self._adjacency_lists)
            if vertex_num in adjacent
        )
        for adjacent in neighbors:
            if not visited[adjacent]:
                self._dfs_mark_weak_component(adjacent, visited)

    def _dfs_mark_island(self, v, visited):
        visited[v] = True
        for adj in self._adjacency_lists[v]:
            if not visited[adj]:
                self._dfs_mark_island(adj, visited)