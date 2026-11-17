"""
Module: graph_adj_matrix.py
Subject: INF310 - Data Structures II
Description: GraphAdjMatrix, a graph stored as an adjacency matrix
             (vertex_list + square 0/1 matrix). Same public API as
             Graph (adjacency list), so both can share the same tests.
             Undirected by default; directed=True gives a digraph.

             Terminology (formal graph theory):
                 order() -> number of vertices
                 size()  -> number of edges

Author: Vladimir
"""

from collections import deque


class GraphAdjMatrix:
    """Adjacency-matrix graph over hashable/comparable vertices."""

    INVALID_VERTEX_NUM = -1

    def __init__(self, vertices=None, directed=False):
        self._vertex_list = []
        self._matrix = []
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
    def adjacency_matrix(self):
        """Copy of the matrix (editing it does not touch the graph)."""
        return [row[:] for row in self._matrix]

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
        self._matrix = [list(row) for row in matrix]

    @property
    def adjacency_list(self):
        """Adjacency list built on the fly from the matrix."""
        return [
            [self._vertex_list[j] for j in self._neighbors(i)]
            for i in range(len(self._vertex_list))
        ]

    @adjacency_list.setter
    def adjacency_list(self, adjacency_list):
        """Replace every edge from a list of neighbor lists. It is
        converted to a matrix and validated by the matrix setter."""
        size = len(self._vertex_list)
        if len(adjacency_list) != size:
            raise ValueError("Adjacency list must have one entry per vertex")
        matrix = [[0] * size for _ in range(size)]
        for i, neighbors in enumerate(adjacency_list):
            for vertex in neighbors:
                j = self._get_num_of_vertex(vertex)
                if j == self.INVALID_VERTEX_NUM:
                    raise ValueError("Vertex not found")
                if matrix[i][j]:
                    raise ValueError("Duplicate neighbor in adjacency list")
                matrix[i][j] = 1
        self.adjacency_matrix = matrix  # checks symmetry if undirected

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
        total = sum(sum(row) for row in self._matrix)
        if self._directed:
            return total
        loops = sum(self._matrix[i][i] for i in range(len(self._matrix)))
        return (total + loops) // 2

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
        for row in self._matrix:
            row.append(0)
        self._matrix.append([0] * len(self._vertex_list))

    def set_vertex(self, old_vertex, new_vertex):
        """Replace a vertex keeping its row and column (its edges)."""
        self._validate_vertex(old_vertex)
        if new_vertex is None:
            raise ValueError("Vertex can't be None")
        old_num = self._get_num_of_vertex(old_vertex)
        new_num = self._get_num_of_vertex(new_vertex)
        if new_num != self.INVALID_VERTEX_NUM and new_num != old_num:
            raise ValueError("Vertex already exists in the Graph")
        self._vertex_list[old_num] = new_vertex

    def exist_vertex(self, vertex):
        if vertex is None:
            raise ValueError("Vertex can't be None")
        return self._get_num_of_vertex(vertex) != self.INVALID_VERTEX_NUM

    def delete_vertex(self, vertex):
        self._validate_vertex(vertex)
        num = self._get_num_of_vertex(vertex)
        self._vertex_list.pop(num)
        self._matrix.pop(num)          # remove its row
        for row in self._matrix:       # remove its column
            row.pop(num)

    def vertex_degree(self, vertex):
        """Out-degree (same as Graph: a loop counts once)."""
        self._validate_vertex(vertex)
        return sum(self._matrix[self._get_num_of_vertex(vertex)])

    def adjacent_of_vertex(self, vertex):
        self._validate_vertex(vertex)
        num = self._get_num_of_vertex(vertex)
        return [self._vertex_list[j] for j in self._neighbors(num)]

    def get_vertex_by_number(self, num_of_vertex):
        if num_of_vertex < 0 or num_of_vertex >= len(self._vertex_list):
            raise ValueError("Invalid number of Vertex")
        return self._vertex_list[num_of_vertex]

    def _neighbors(self, index):
        """Indices of the neighbors of a vertex, ascending."""
        return [j for j, value in enumerate(self._matrix[index]) if value]

    def _validate_vertex(self, vertex):
        if vertex is None:
            raise ValueError("Vertex can't be None")
        if self._get_num_of_vertex(vertex) == self.INVALID_VERTEX_NUM:
            raise ValueError("Vertex not found")

    def _get_num_of_vertex(self, vertex):
        for i, current in enumerate(self._vertex_list):
            if current == vertex:
                return i
        return self.INVALID_VERTEX_NUM

    # ------------------------------------------------------------------
    # Edge methods
    # ------------------------------------------------------------------
    def insert_edge(self, origin_vertex, destination_vertex):
        if self.exist_adjacency(origin_vertex, destination_vertex):
            raise ValueError("Edge already exists in the graph")
        i = self._get_num_of_vertex(origin_vertex)
        j = self._get_num_of_vertex(destination_vertex)
        self._matrix[i][j] = 1
        if not self._directed:
            self._matrix[j][i] = 1

    def delete_edge(self, origin_vertex, destination_vertex):
        self._validate_vertex(origin_vertex)
        self._validate_vertex(destination_vertex)
        i = self._get_num_of_vertex(origin_vertex)
        j = self._get_num_of_vertex(destination_vertex)
        self._matrix[i][j] = 0
        if not self._directed:
            self._matrix[j][i] = 0

    def exist_adjacency(self, origin_vertex, destination_vertex):
        self._validate_vertex(origin_vertex)
        self._validate_vertex(destination_vertex)
        i = self._get_num_of_vertex(origin_vertex)
        j = self._get_num_of_vertex(destination_vertex)
        return self._matrix[i][j] == 1

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
        for adj in self._neighbors(vertex_num):
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
                for adj in reversed(self._neighbors(vertex_num)):
                    if not marked[adj]:
                        stack.append(adj)
        return visited

    def bfs(self, start_vertex):
        self._validate_vertex(start_vertex)
        visited = []
        marked = [False] * len(self._vertex_list)
        start_num = self._get_num_of_vertex(start_vertex)
        queue = deque([start_num])
        marked[start_num] = True
        while queue:
            vertex_num = queue.popleft()
            visited.append(self._vertex_list[vertex_num])
            for adj in self._neighbors(vertex_num):
                if not marked[adj]:
                    marked[adj] = True
                    queue.append(adj)
        return visited

    def is_reachable(self, origin, destination):
        self._validate_vertex(origin)
        self._validate_vertex(destination)
        return destination in self.bfs(origin)

    # ------------------------------------------------------------------
    # Cycles and components
    # ------------------------------------------------------------------
    def has_cycle(self):
        size = len(self._vertex_list)
        if self._directed:
            state = [0] * size  # 0 new, 1 in stack, 2 done
            return any(
                state[v] == 0 and self._dfs_directed_cycle(v, state)
                for v in range(size)
            )
        visited = [False] * size
        return any(
            not visited[v] and self._dfs_cycle_undirected(v, -1, visited)
            for v in range(size)
        )

    def _dfs_cycle_undirected(self, v, parent, visited):
        visited[v] = True
        for adj in self._neighbors(v):
            if not visited[adj]:
                if self._dfs_cycle_undirected(adj, v, visited):
                    return True
            elif adj != parent:
                return True
        return False

    def _dfs_directed_cycle(self, v, state):
        state[v] = 1
        for adj in self._neighbors(v):
            if state[adj] == 1:
                return True
            if state[adj] == 0 and self._dfs_directed_cycle(adj, state):
                return True
        state[v] = 2
        return False

    def count_islands(self):
        """Connected components (weakly connected if directed)."""
        size = len(self._vertex_list)
        visited = [False] * size
        count = 0
        for v in range(size):
            if not visited[v]:
                count += 1
                self._mark_component(v, visited)
        return count

    def _mark_component(self, v, visited):
        visited[v] = True
        neighbors = set(self._neighbors(v))
        if self._directed:
            neighbors.update(
                i for i in range(len(self._matrix)) if self._matrix[i][v]
            )
        for adj in neighbors:
            if not visited[adj]:
                self._mark_component(adj, visited)