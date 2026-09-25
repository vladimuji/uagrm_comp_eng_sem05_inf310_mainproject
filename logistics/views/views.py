from django.conf import settings
from django.views.generic import TemplateView


class BaseView(TemplateView):
    template_name = "logistics/index.html"


class TreeView(TemplateView):
    template_name = "logistics/tree_view.html"


class HeapView(TemplateView):
    template_name = "logistics/heap_view.html"


class GraphView(TemplateView):
    template_name = "logistics/graph_view.html"


class MapView(TemplateView):
    template_name = "logistics/map_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["google_maps_api_key"] = settings.GOOGLE_MAPS_API_KEY
        return context