"""Interface shared by heap implementations."""

from abc import ABC, abstractmethod


class IHeap(ABC):
    """Public operations required of a heap."""

    @abstractmethod
    def insert(self, data):
        pass

    @abstractmethod
    def extract_root(self):
        pass

    @abstractmethod
    def peek_root(self):
        pass

    @abstractmethod
    def is_empty(self):
        pass

    @abstractmethod
    def size(self):
        pass

    @abstractmethod
    def empty(self):
        pass

    @abstractmethod
    def build_heap(self, data):
        pass

    @abstractmethod
    def has_priority(self, a, b):
        pass
