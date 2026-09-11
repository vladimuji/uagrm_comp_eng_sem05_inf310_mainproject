"""
logistics/services/tree_service.py

Extends the original AVL/BST service with:
  - B-way tree (BMWayTree)   -> DB-backed, stores raw int IDs
  - M-way tree (MWaySearchTree) -> DB-backed, stores raw int IDs
  - Expression tree           -> ephemeral, no DB, no persistence
"""

from datastructures.data.city_node import CityNode
from datastructures.bin_tree.avl_tree import AVLTree
from datastructures.bin_tree.search_binary_tree import SearchBinaryTree
from datastructures.bin_tree.bmway_tree import BMWayTree
from datastructures.bin_tree.mway_search_tree import MWaySearchTree
from datastructures.bin_tree.expression_tree import ExpressionTree
from logistics.models import Node

# ----------------------------------------------------------------------
# Tree registries
# ----------------------------------------------------------------------
BINARY_TREE_CLASSES = {"avl": AVLTree, "bst": SearchBinaryTree}
MWAY_TREE_CLASSES = {"bway": BMWayTree, "mway": MWaySearchTree}
TREE_CLASSES = {**BINARY_TREE_CLASSES, **MWAY_TREE_CLASSES}

DEFAULT_SORT_KEY = "id"
DEFAULT_ORDER = 4


class TreeNotFound(Exception):
    pass


class NodeAlreadyExists(Exception):
    pass


class NodeNotFound(Exception):
    pass


def _is_mway(kind):
    return kind in MWAY_TREE_CLASSES


def _resolve_tree_class(kind):
    tree_cls = TREE_CLASSES.get(kind)
    if tree_cls is None:
        raise TreeNotFound(kind)
    return tree_cls


# ----------------------------------------------------------------------
# Build / insert / delete
# ----------------------------------------------------------------------
def build_tree(kind, sort_key=DEFAULT_SORT_KEY, order=DEFAULT_ORDER):
    tree_cls = _resolve_tree_class(kind)

    if _is_mway(kind):
        tree = tree_cls(order)
        ids = Node.objects.order_by("id").values_list("id", flat=True)
        for node_id in ids:
            tree.insert(node_id)
        return tree

    tree = tree_cls()
    rows = Node.objects.order_by("id").values()
    for row in rows:
        tree.insert(CityNode(**row, sort_key=sort_key))
    return tree


def _find_by_id(tree, node_id):
    """Traversal-based lookup by id for CityNode-based trees (AVL/BST)."""
    for node in tree.iteration_by_levels():
        if node.id == node_id:
            return node
    return None


def _apply_default_fields(node_id, extra_fields):
    """Fill in sensible defaults for any optional field the user omitted."""
    fields = dict(extra_fields or {})
    fields.setdefault("city_name", f"city_{node_id}")
    fields.setdefault("state", f"state_{node_id}")
    fields.setdefault("latitude", 0.0)
    fields.setdefault("longitude", 0.0)
    fields.setdefault("listed", False)
    return fields


def insert_node(kind, node_id, sort_key=DEFAULT_SORT_KEY,
                 extra_fields=None, order=DEFAULT_ORDER):
    tree = build_tree(kind, sort_key, order)

    if _is_mway(kind):
        if tree.has(node_id):
            raise NodeAlreadyExists(node_id)
    else:
        if _find_by_id(tree, node_id) is not None:
            raise NodeAlreadyExists(node_id)

    fields = _apply_default_fields(node_id, extra_fields)
    Node.objects.create(id=node_id, **fields)

    if _is_mway(kind):
        tree.insert(node_id)
    else:
        row = Node.objects.values().get(id=node_id)
        tree.insert(CityNode(**row, sort_key=sort_key))
    return tree


def delete_node(kind, node_id, sort_key=DEFAULT_SORT_KEY, order=DEFAULT_ORDER):
    tree = build_tree(kind, sort_key, order)

    if _is_mway(kind):
        if not tree.has(node_id):
            raise NodeNotFound(node_id)
        delete_target = node_id
    else:
        delete_target = _find_by_id(tree, node_id)
        if delete_target is None:
            raise NodeNotFound(node_id)

    deleted_count, _ = Node.objects.filter(id=node_id).delete()
    if deleted_count == 0:
        raise NodeNotFound(node_id)

    tree.delete(delete_target)  # int for bway/mway, CityNode for avl/bst
    return tree


# ----------------------------------------------------------------------
# Serialization
# ----------------------------------------------------------------------
def serialize_tree(tree, kind):
    if _is_mway(kind):
        return serialize_mway_tree(tree)
    return serialize_binary_tree(tree)


def serialize_binary_tree(tree):
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
    """Binary-heap-indexed flat array (root at 0, children at 2i+1/2i+2).
    Only meaningful for AVL/BST (fixed left/right child shape)."""
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


def serialize_mway_tree(tree):
    """B-way / M-way trees hold raw int IDs and a variable number of
    children per node, so they get a nested {keys, children} structure
    instead of the fixed binary-heap array."""
    ids_in_tree = tree.iteration_by_levels()
    return {
        "structure": _serialize_mway_node(tree.root),
        "in_order": tree.in_order(),
        "pre_order": tree.pre_order(),
        "post_order": tree.post_order(),
        "levels": ids_in_tree,
        "height": tree.high(),
        "size": tree.size(),
        "order": tree.order,
        "node_info": _build_node_info_map(ids_in_tree),
    }


def _serialize_mway_node(node):
    if node is None:
        return None
    return {
        "keys": list(node.keys),
        "children": [_serialize_mway_node(child) for child in node.children],
    }


def _build_node_info_map(ids):
    """id -> full row dict, for frontend hover tooltips."""
    if not ids:
        return {}
    rows = Node.objects.filter(id__in=ids).values()
    return {row["id"]: row for row in rows}


# ----------------------------------------------------------------------
# Expression tree (ephemeral: infix in, evaluated tree out, no DB)
# ----------------------------------------------------------------------
def evaluate_expression(infix_expression):
    tree = ExpressionTree.from_infix(infix_expression)
    return {
        "structure": _serialize_generic_structure(tree),
        "infix": ExpressionTree.list_to_string(tree.in_order()),
        "prefix": ExpressionTree.list_to_string(tree.pre_order()),
        "postfix": ExpressionTree.list_to_string(tree.post_order()),
        "result": tree.evaluate(),
        "height": tree.high(),
        "size": tree.size(),
    }


def _serialize_generic_structure(tree):
    """Same binary-heap indexing as serialize_structure, but for nodes
    whose data is a plain float/str (ExpressionNode) instead of CityNode."""
    height = tree.high()
    size = (2 ** height) - 1 if height else 0
    array = [None] * size

    def walk(node, index):
        if node is None or index >= size:
            return
        array[index] = node.data
        walk(node.left_child, 2 * index + 1)
        walk(node.right_child, 2 * index + 2)

    walk(tree.root, 0)
    return array