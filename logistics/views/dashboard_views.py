from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/dashboard.html"


class CargoServicesView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/operations/cargo_services.html"


class PaymentsView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/operations/payments.html"


class CustomersView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/people/customers.html"


class DriversView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/people/drivers.html"


class CarOwnersView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/people/car_owners.html"


class StaffView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/people/staff.html"


class VehiclesView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/fleet/vehicles.html"


class ZonesView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/geography/zones.html"


class CitiesView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/geography/cities.html"


class RoutesView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/geography/routes.html"


class RouteMapView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/geography/route_map.html"


class ServiceStatusesView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/catalogs/service_statuses.html"


class PaymentMethodsView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/catalogs/payment_methods.html"


class AuditLogView(LoginRequiredMixin, TemplateView):
    template_name = "logistics/admin/system/audit_log.html"





