"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from logistics.views import BaseView, TreeView, GraphView, HeapView, MapView, TicTacToeView
# from logistics.views.api_views import TreeOperationView, ExpressionTreeView, GraphDataView
from logistics.views.api_views import (
    TreeOperationView, ExpressionTreeView, GraphDataView,
    GameCreateView, GameDetailView, GameMoveView,
)
from logistics.views.system_views import RestoreDatabaseView
from django.contrib.auth import views as auth_views
from logistics.views.dashboard_views import (
    DashboardView,
    CargoServicesView,
    PaymentsView,
    CustomersView,
    DriversView,
    CarOwnersView,
    StaffView,
    VehiclesView,
    ZonesView,
    CitiesView,
    RoutesView,
    RouteMapView,
    ServiceStatusesView,
    PaymentMethodsView,
    AuditLogView,
)
from logistics.views.dashboard_api_views import (
    DashboardKpisApiView,
    FleetAvailabilityApiView,
    PendingBalancesApiView,
    RevenueByMonthApiView,
    ServicesByTypeApiView,
    RecentServicesApiView,
)
from logistics.views.cargo_services_api_views import (
    CargoServiceListCreateApiView,
    CargoServiceDetailApiView,
    CargoServiceAssignDriverApiView,
    CargoServiceChangeStatusApiView,
    CargoServiceKpisApiView,
    UnassignedCargoServicesApiView,
    SimpleCustomersApiView,
    CargoServiceZonesApiView,
    CargoServiceStatusesApiView,
    AvailableDriversApiView,
    SuggestedCargoServicePriceApiView,
    CargoServiceCountByStatusApiView,
)
from logistics.views.payments_api_views import (
    PaymentReceiptListCreateApiView,
    PaymentReceiptDetailApiView,
    PaymentKpisByMethodApiView,
    CargoServicesWithBalanceApiView,
    PaymentRevenueVariationApiView,
    PaymentMethodsForReceiptApiView,
)
from logistics.views.api_views import (
    TreeOperationView, ExpressionTreeView, GraphDataView,
    GameCreateView, GameDetailView, GameMoveView, GraphDemoView,
)

urlpatterns = [
    path('', BaseView.as_view(), name='home'),
    path('base/', BaseView.as_view()),
    path('trees/', TreeView.as_view(), name='trees'),
    path('graphs/', GraphView.as_view(), name='graphs'),
    path('heaps/', HeapView.as_view(), name='heaps'),
    path('admin/', admin.site.urls),

    # expression tree -> ephemeral, no DB, no 'kind'
    path('api/trees/expression/', ExpressionTreeView.as_view(), name='expression-tree-api'),
    
    # avl / bst / bway / mway -> DB-backed CRUD-ish endpoint
    path('api/trees/<str:kind>/', TreeOperationView.as_view(), name='tree-api'),
 
    path('system/restore/<str:token>/', RestoreDatabaseView.as_view(), name='restore-db'),

    path('map/', MapView.as_view(), name='map'),
    path('api/graph/', GraphDataView.as_view(), name='graph-api'),
    path('api/graphs/<str:kind>/', GraphDemoView.as_view(), name='graph-demo-api'),

    # For the TicTacToe Game
    path('tictactoe/', TicTacToeView.as_view(), name='tictactoe'),
    path('api/game/', GameCreateView.as_view(), name='game-create'),
    path('api/game/<int:game_id>/', GameDetailView.as_view(), name='game-detail'),
    path('api/game/<int:game_id>/move/', GameMoveView.as_view(), name='game-move'),

    # Dashboard datasets are served by SQL Server stored procedures/functions.
    path('api/dashboard/kpis/', DashboardKpisApiView.as_view(), name='dashboard-kpis-api'),
    path('api/dashboard/fleet-availability/', FleetAvailabilityApiView.as_view(), name='dashboard-fleet-availability-api'),
    path('api/dashboard/pending-balances/', PendingBalancesApiView.as_view(), name='dashboard-pending-balances-api'),
    path('api/dashboard/revenue-by-month/', RevenueByMonthApiView.as_view(), name='dashboard-revenue-by-month-api'),
    path('api/dashboard/services-by-type/', ServicesByTypeApiView.as_view(), name='dashboard-services-by-type-api'),
    path('api/dashboard/recent-services/', RecentServicesApiView.as_view(), name='dashboard-recent-services-api'),

    # Cargo-service operations are backed by SQL Server procedures/functions.
    path('api/operations/cargo-services/', CargoServiceListCreateApiView.as_view(), name='cargo-service-list-create-api'),
    path('api/operations/cargo-services/kpis/', CargoServiceKpisApiView.as_view(), name='cargo-service-kpis-api'),
    path('api/operations/cargo-services/unassigned/', UnassignedCargoServicesApiView.as_view(), name='cargo-service-unassigned-api'),
    path('api/operations/cargo-services/customers/', SimpleCustomersApiView.as_view(), name='cargo-service-customers-api'),
    path('api/operations/cargo-services/zones/', CargoServiceZonesApiView.as_view(), name='cargo-service-zones-api'),
    path('api/operations/cargo-services/statuses/', CargoServiceStatusesApiView.as_view(), name='cargo-service-statuses-api'),
    path('api/operations/cargo-services/drivers/available/', AvailableDriversApiView.as_view(), name='cargo-service-drivers-available-api'),
    path('api/operations/cargo-services/suggest-price/', SuggestedCargoServicePriceApiView.as_view(), name='cargo-service-suggest-price-api'),
    path('api/operations/cargo-services/count-by-status/', CargoServiceCountByStatusApiView.as_view(), name='cargo-service-count-by-status-api'),
    path('api/operations/cargo-services/<int:service_id>/', CargoServiceDetailApiView.as_view(), name='cargo-service-detail-api'),
    path('api/operations/cargo-services/<int:service_id>/assign-driver/', CargoServiceAssignDriverApiView.as_view(), name='cargo-service-assign-driver-api'),
    path('api/operations/cargo-services/<int:service_id>/status/', CargoServiceChangeStatusApiView.as_view(), name='cargo-service-change-status-api'),

    # Payment receipts and summaries are backed by SQL Server.
    path('api/operations/payments/', PaymentReceiptListCreateApiView.as_view(), name='payment-receipt-list-create-api'),
    path('api/operations/payments/kpis-by-method/', PaymentKpisByMethodApiView.as_view(), name='payment-kpis-by-method-api'),
    path('api/operations/payments/revenue-variation/', PaymentRevenueVariationApiView.as_view(), name='payment-revenue-variation-api'),
    path('api/operations/payments/services-with-balance/', CargoServicesWithBalanceApiView.as_view(), name='payment-services-with-balance-api'),
    path('api/operations/payments/methods/', PaymentMethodsForReceiptApiView.as_view(), name='payment-methods-for-receipt-api'),
    path('api/operations/payments/<int:receipt_number>/', PaymentReceiptDetailApiView.as_view(), name='payment-receipt-detail-api'),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
        template_name='logistics/admin/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/operations/cargo-services/', CargoServicesView.as_view(), name='cargo-services'),
    path('dashboard/operations/payments/', PaymentsView.as_view(), name='payments'),
    path('dashboard/people/customers/', CustomersView.as_view(), name='customers'),
    path('dashboard/people/drivers/', DriversView.as_view(), name='drivers'),
    path('dashboard/people/car-owners/', CarOwnersView.as_view(), name='car-owners'),
    path('dashboard/people/staff/', StaffView.as_view(), name='staff'),
    path('dashboard/fleet/vehicles/', VehiclesView.as_view(), name='vehicles'),
    path('dashboard/geography/zones/', ZonesView.as_view(), name='zones'),
    path('dashboard/geography/cities/', CitiesView.as_view(), name='cities'),
    path('dashboard/geography/routes/', RoutesView.as_view(), name='routes'),
    path('dashboard/geography/route-map/', RouteMapView.as_view(), name='route-map'),
    path('dashboard/catalogs/service-statuses/', ServiceStatusesView.as_view(), name='service-statuses'),
    path('dashboard/catalogs/payment-methods/', PaymentMethodsView.as_view(), name='payment-methods'),
    path('dashboard/system/audit-log/', AuditLogView.as_view(), name='audit-log'),
]
