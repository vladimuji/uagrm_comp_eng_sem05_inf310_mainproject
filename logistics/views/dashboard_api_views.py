import logging

from django.db import DatabaseError
from django.http import JsonResponse
from django.views import View

from logistics.services import dashboard_service

logger = logging.getLogger(__name__)


class DashboardApiView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        return super().dispatch(request, *args, **kwargs)

    def get_data(self, request):
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        try:
            return JsonResponse(self.get_data(request), safe=False)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)
        except dashboard_service.DashboardResultShapeError:
            logger.exception("Dashboard API received an unexpected SQL result")
            return JsonResponse(
                {"error": "Dashboard data could not be loaded"},
                status=500,
            )
        except DatabaseError:
            logger.exception("Dashboard API database request failed")
            return JsonResponse(
                {"error": "Dashboard data could not be loaded"},
                status=500,
            )


class DashboardKpisApiView(DashboardApiView):
    def get_data(self, request):
        return dashboard_service.get_dashboard_kpis()


class FleetAvailabilityApiView(DashboardApiView):
    def get_data(self, request):
        return dashboard_service.get_fleet_availability()


class PendingBalancesApiView(DashboardApiView):
    def get_data(self, request):
        return dashboard_service.get_pending_balances()


class RevenueByMonthApiView(DashboardApiView):
    def get_data(self, request):
        months = _positive_query_integer(request, "months", default=6)
        return dashboard_service.get_revenue_by_month(months)


class ServicesByTypeApiView(DashboardApiView):
    def get_data(self, request):
        return dashboard_service.get_services_by_type()


class RecentServicesApiView(DashboardApiView):
    def get_data(self, request):
        top_n = _positive_query_integer(request, "top_n", default=5)
        return dashboard_service.get_recent_services(top_n)


def _positive_query_integer(request, parameter_name, default):
    raw_value = request.GET.get(parameter_name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        raise ValueError(
            "'{}' must be a positive integer.".format(parameter_name)
        )
    if value <= 0:
        raise ValueError(
            "'{}' must be a positive integer.".format(parameter_name)
        )
    return value
