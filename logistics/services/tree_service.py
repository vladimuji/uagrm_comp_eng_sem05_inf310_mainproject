import sys

from datastructures.data.city_node import CityNode
from datastructures.bin_tree.avl_tree import AVLTree
from datastructures.bin_tree.search_binary_tree import SearchBinaryTree
from logistics.models import Node

TREE_CLASSES = {"avl": AVLTree, "bst": SearchBinaryTree}
DEFAULT_SORT_KEY = "id"


class TreeNotFound(Exception): pass
class NodeAlreadyExists(Exception): pass
class NodeNotFound(Exception): pass


def _resolve_tree_class(kind):
    tree_cls = TREE_CLASSES.get(kind)
    if tree_cls is None:
        raise TreeNotFound(kind)
    return tree_cls


def build_tree(kind, sort_key=DEFAULT_SORT_KEY):
    tree_cls = _resolve_tree_class(kind)
    tree = tree_cls()
    rows = Node.objects.order_by("id").values()
    for row in rows:
        tree.insert(CityNode(**row, sort_key=sort_key))
    return tree


def _find_by_id(tree, node_id):
    """Traversal-based lookup by id — correct regardless of sort_key,
    unlike BST navigation which assumes ordering == identity."""
    for node in tree.iteration_by_levels():
        if node.id == node_id:
            return node
    return None


def insert_node(kind, node_id, sort_key=DEFAULT_SORT_KEY, extra_fields=None):
    tree = build_tree(kind, sort_key)

    if _find_by_id(tree, node_id) is not None:
        raise NodeAlreadyExists(node_id)

    Node.objects.create(id=node_id, **(extra_fields or {}))

    row = Node.objects.values().get(id=node_id)
    tree.insert(CityNode(**row, sort_key=sort_key))
    return tree


def delete_node(kind, node_id, sort_key=DEFAULT_SORT_KEY):
    tree = build_tree(kind, sort_key)

    target = _find_by_id(tree, node_id)
    if target is None:
        raise NodeNotFound(node_id)

    deleted_count, _ = Node.objects.filter(id=node_id).delete()
    if deleted_count == 0:
        raise NodeNotFound(node_id)

    tree.delete(target)  # target already carries the real sort_key value
    return tree


def serialize_tree(tree):
    return {
        "structure": serialize_structure(tree),
        "in_order": [c.to_dict() for c in tree.in_order()],
        "pre_order": [c.to_dict() for c in tree.pre_order()],
        "post_order": [c.to_dict() for c in tree.post_order()],
        "levels": [c.to_dict() for c in tree.iteration_by_levels()],
        "height": tree.high(),
        "size": tree.size(),
    }


def serialize_structure(tree):
    height = tree.high()
    size = (2 ** height) - 1 if height else 0
    array = [None] * size

    def walk(node, index):
        if node is None or index >= size:
            return
        array[index] = node.data.to_dict()
        walk(node.left_child, 2 * index + 1)
        walk(node.right_child, 2 * index + 2)

    walk(tree.root, 0)
    return array