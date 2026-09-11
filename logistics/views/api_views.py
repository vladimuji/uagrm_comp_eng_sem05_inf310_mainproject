import json

from django.db import IntegrityError
from django.http import JsonResponse
from django.views import View

from logistics.services import tree_service

ALLOWED_SORT_KEYS = {"id", "city_name"}
DEFAULT_SORT_KEY = "id"

DEFAULT_ORDER = 4
MIN_ORDER = 3
MAX_ORDER = 10


def _resolve_sort_key(raw_value):
    sort_key = raw_value or DEFAULT_SORT_KEY
    return sort_key if sort_key in ALLOWED_SORT_KEYS else None


def _resolve_order(raw_value):
    """Only matters for bway/mway; harmless (unused) for avl/bst."""
    if raw_value in (None, ""):
        return DEFAULT_ORDER
    try:
        order = int(raw_value)
    except (TypeError, ValueError):
        return None
    if order < MIN_ORDER or order > MAX_ORDER:
        return None
    return order


class TreeOperationView(View):
    def get(self, request, kind):
        sort_key = _resolve_sort_key(request.GET.get("sort_by"))
        if sort_key is None:
            return JsonResponse({"error": "Invalid 'sort_by'"}, status=400)
        order = _resolve_order(request.GET.get("order"))
        if order is None:
            return JsonResponse({"error": "Invalid 'order'"}, status=400)
        try:
            tree = tree_service.build_tree(kind, sort_key, order)
        except tree_service.TreeNotFound:
            return JsonResponse({"error": f"Unknown tree kind '{kind}'"}, status=404)
        return JsonResponse(tree_service.serialize_tree(tree, kind))

    def post(self, request, kind):
        payload = json.loads(request.body or "{}")
        node_id = payload.get("id")
        if node_id is None:
            return JsonResponse({"error": "Missing 'id'"}, status=400)
        sort_key = _resolve_sort_key(payload.get("sort_by"))
        if sort_key is None:
            return JsonResponse({"error": "Invalid 'sort_by'"}, status=400)
        order = _resolve_order(payload.get("order"))
        if order is None:
            return JsonResponse({"error": "Invalid 'order'"}, status=400)
        try:
            tree = tree_service.insert_node(
                kind, node_id, sort_key, payload.get("extra_fields"), order
            )
        except tree_service.TreeNotFound:
            return JsonResponse({"error": f"Unknown tree kind '{kind}'"}, status=404)
        except tree_service.NodeAlreadyExists:
            return JsonResponse({"error": f"ID {node_id} already exists"}, status=409)
        except IntegrityError:
            return JsonResponse({"error": "DB insert failed"}, status=500)
        return JsonResponse(tree_service.serialize_tree(tree, kind), status=201)

    def delete(self, request, kind):
        payload = json.loads(request.body or "{}")
        node_id = payload.get("id")
        if node_id is None:
            return JsonResponse({"error": "Missing 'id'"}, status=400)
        sort_key = _resolve_sort_key(payload.get("sort_by"))
        if sort_key is None:
            return JsonResponse({"error": "Invalid 'sort_by'"}, status=400)
        order = _resolve_order(payload.get("order"))
        if order is None:
            return JsonResponse({"error": "Invalid 'order'"}, status=400)
        try:
            tree = tree_service.delete_node(kind, node_id, sort_key, order)
        except tree_service.TreeNotFound:
            return JsonResponse({"error": f"Unknown tree kind '{kind}'"}, status=404)
        except tree_service.NodeNotFound:
            return JsonResponse({"error": f"ID {node_id} not found"}, status=404)
        return JsonResponse(tree_service.serialize_tree(tree, kind))


class ExpressionTreeView(View):
    """Ephemeral: no DB read/write, no 'kind' dispatch. Just build+evaluate
    an infix expression on every request."""

    def post(self, request):
        payload = json.loads(request.body or "{}")
        infix = payload.get("infix")
        if not infix:
            return JsonResponse({"error": "Missing 'infix'"}, status=400)
        try:
            result = tree_service.evaluate_expression(infix)
        except (ValueError, ZeroDivisionError, IndexError) as error:
            return JsonResponse({"error": str(error)}, status=400)
        return JsonResponse(result)