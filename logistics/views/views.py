from django.views.generic import TemplateView


class BaseView(TemplateView):
    template_name = "logistics/index.html"


class TreeView(TemplateView):
    template_name = "logistics/tree_view.html"


class HeapView(TemplateView):
    template_name = "logistics/heap_view.html"


class GraphView(TemplateView):
    template_name = "logistics/graph_view.html"
