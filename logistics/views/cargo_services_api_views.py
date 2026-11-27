import json
import logging
import re
from datetime import timezone as datetime_timezone
from decimal import Decimal, InvalidOperation

from django.db import DatabaseError
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.views import View

from logistics.services import cargo_services_service
from logistics.services.sql_result_service import SqlResultShapeError

logger = logging.getLogger(__name__)

BUSINESS_ERROR_STATUSES = {
    51001: 400,
    51002: 400,
    51003: 404,
    51004: 400,
    51005: 400,
    51006: 400,
    51007: 400,
    51008: 400,
    51009: 409,
    51010: 409,
    51011: 400,
    51012: 404,
    51013: 409,
    51014: 409,
    51015: 409,
    51016: 409,
    51017: 404,
    51018: 409,
    51019: 409,
    51020: 400,
    51021: 409,
    51022: 409,
    51023: 404,
    51024: 400,
    51025: 409,
    51026: 409,
    51027: 409,
    51028: 400,
}


def _parse_sql_business_error(error):
    error_text = " ".join(str(argument) for argument in error.args)
    match = re.search(r"\((510\d{2})\)", error_text)
    if match is None:
        return None

    error_code = int(match.group(1))
    status_code = BUSINESS_ERROR_STATUSES.get(error_code)
    if status_code is None:
        return None

    message_match = re.search(
        r"\[SQL Server\](.*?)\s+\(" + str(error_code) + r"\)",
        error_text,
        re.DOTALL,
    )
    message = (
        message_match.group(1).strip()
        if message_match
        else "SQL Server rechazó la operación."
    )
    return error_code, status_code, message


def _request_payload(request):
    try:
        payload = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Request body must contain valid JSON.")
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")
    return payload


def _parse_integer(value, name):
    if isinstance(value, bool):
        raise ValueError("{} must be a positive integer.".format(name))
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError("{} must be a positive integer.".format(name))
    if (
        parsed <= 0
        or parsed > cargo_services_service.MAX_SQL_INT
        or str(parsed) != str(value).strip()
    ):
        raise ValueError("{} must be a positive integer.".format(name))
    return parsed


def _required_text(payload, name, max_length):
    value = payload.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError("'{}' is required.".format(name))
    value = value.strip()
    if len(value) > max_length:
        raise ValueError("'{}' exceeds {} characters.".format(name, max_length))
    return value


def _parse_datetime(value, name):
    parsed = parse_datetime(value) if isinstance(value, str) else None
    if parsed is None:
        raise ValueError("'{}' must be an ISO date and time.".format(name))
    if timezone.is_aware(parsed):
        parsed = timezone.make_naive(parsed, datetime_timezone.utc)
    return parsed


def _parse_date_query(request, name):
    value = request.GET.get(name)
    if value in (None, ""):
        return None
    parsed = parse_date(value)
    if parsed is None:
        raise ValueError("'{}' must be an ISO date.".format(name))
    return parsed


def _parse_optional_query_integer(request, name):
    value = request.GET.get(name)
    if value in (None, ""):
        return None
    return _parse_integer(value, name)


def _parse_money(value, name="agreed_price"):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("'{}' must be a valid amount.".format(name))
    if not amount.is_finite() or amount < 0:
        raise ValueError("'{}' must be zero or greater.".format(name))
    return amount


def _business_error_response(error):
    business_error = _parse_sql_business_error(error)
    if business_error is None:
        logger.exception("Cargo-service SQL operation failed")
        return JsonResponse(
            {"error": "Cargo-service operation could not be completed"},
            status=500,
        )

    error_code, status_code, message = business_error
    logger.warning("Cargo-service operation rejected by SQL rule %s", error_code)
    return JsonResponse(
        {"error": message, "code": error_code},
        status=status_code,
    )


class CargoServicesApiView(View):
    post_status = 200

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        return super().dispatch(request, *args, **kwargs)

    def get_data(self, request, **kwargs):
        raise NotImplementedError

    def post_data(self, request, payload, **kwargs):
        raise NotImplementedError

    def put_data(self, request, payload, **kwargs):
        raise NotImplementedError

    def _respond(self, callback, status=200):
        try:
            return JsonResponse(callback(), safe=False, status=status)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)
        except SqlResultShapeError:
            logger.exception("Cargo-service SQL result had an unexpected shape")
            return JsonResponse(
                {"error": "Cargo-service data could not be loaded"},
                status=500,
            )
        except DatabaseError as error:
            return _business_error_response(error)

    def get(self, request, *args, **kwargs):
        return self._respond(lambda: self.get_data(request, **kwargs))

    def post(self, request, *args, **kwargs):
        return self._respond(
            lambda: self.post_data(request, _request_payload(request), **kwargs),
            status=self.post_status,
        )

    def put(self, request, *args, **kwargs):
        return self._respond(
            lambda: self.put_data(request, _request_payload(request), **kwargs)
        )


class CargoServiceListCreateApiView(CargoServicesApiView):
    post_status = 201

    def get_data(self, request):
        return cargo_services_service.list_cargo_services(
            date_from=_parse_date_query(request, "date_from"),
            date_to=_parse_date_query(request, "date_to"),
            customer_id=_parse_optional_query_integer(request, "customer_id"),
            driver_id=_parse_optional_query_integer(request, "driver_id"),
            status_id=_parse_optional_query_integer(request, "status_id"),
            page_number=_parse_integer(
                request.GET.get("page", "1"), "page"
            ),
            page_size=_parse_integer(
                request.GET.get("page_size", "20"), "page_size"
            ),
        )

    def post_data(self, request, payload):
        driver_id = payload.get("driver_id")
        if driver_id in ("", None):
            driver_id = None
        else:
            driver_id = _parse_integer(driver_id, "driver_id")

        return cargo_services_service.create_cargo_service(
            customer_id=_parse_integer(payload.get("customer_id"), "customer_id"),
            zone_id=_parse_integer(payload.get("zone_id"), "zone_id"),
            cargo_type_id=_parse_integer(
                payload.get("cargo_type_id"), "cargo_type_id"
            ),
            cargo_detail=_required_text(payload, "cargo_detail", 200),
            origin=_required_text(payload, "origin", 100),
            destination=_required_text(payload, "destination", 100),
            date_time_scheduled=_parse_datetime(
                payload.get("date_time_scheduled"),
                "date_time_scheduled",
            ),
            agreed_price=_parse_money(payload.get("agreed_price")),
            driver_id=driver_id,
        )


class CargoServiceDetailApiView(CargoServicesApiView):
    def get_data(self, request, service_id):
        return cargo_services_service.get_cargo_service(service_id)

    def put_data(self, request, payload, service_id):
        return cargo_services_service.update_cargo_service(
            service_id=service_id,
            cargo_detail=_required_text(payload, "cargo_detail", 200),
            date_time_scheduled=_parse_datetime(
                payload.get("date_time_scheduled"),
                "date_time_scheduled",
            ),
            agreed_price=_parse_money(payload.get("agreed_price")),
        )


class CargoServiceAssignDriverApiView(CargoServicesApiView):
    def post_data(self, request, payload, service_id):
        return cargo_services_service.assign_cargo_service_driver(
            service_id,
            _parse_integer(payload.get("driver_id"), "driver_id"),
        )


class CargoServiceChangeStatusApiView(CargoServicesApiView):
    def post_data(self, request, payload, service_id):
        return cargo_services_service.change_cargo_service_status(
            service_id,
            _parse_integer(payload.get("new_status"), "new_status"),
        )


class CargoServiceKpisApiView(CargoServicesApiView):
    def get_data(self, request):
        return cargo_services_service.get_cargo_service_kpis()


class UnassignedCargoServicesApiView(CargoServicesApiView):
    def get_data(self, request):
        return cargo_services_service.get_unassigned_cargo_services()


class SimpleCustomersApiView(CargoServicesApiView):
    def get_data(self, request):
        return cargo_services_service.list_customers_simple()


class CargoServiceZonesApiView(CargoServicesApiView):
    def get_data(self, request):
        return cargo_services_service.list_zones_for_cargo_service()


class CargoServiceStatusesApiView(CargoServicesApiView):
    def get_data(self, request):
        return cargo_services_service.list_service_statuses()


class AvailableDriversApiView(CargoServicesApiView):
    def get_data(self, request):
        date_time = _parse_datetime(
            request.GET.get("date_time"),
            "date_time",
        )
        return cargo_services_service.list_available_drivers(date_time)


class SuggestedCargoServicePriceApiView(CargoServicesApiView):
    def get_data(self, request):
        origin_node = _parse_integer(
            request.GET.get("origin_node"),
            "origin_node",
        )
        destination_node = _parse_integer(
            request.GET.get("destination_node"),
            "destination_node",
        )
        return cargo_services_service.get_suggested_cargo_service_price(
            origin_node,
            destination_node,
        )


class CargoServiceCountByStatusApiView(CargoServicesApiView):
    def get_data(self, request):
        month = _parse_optional_query_integer(request, "month")
        year = _parse_optional_query_integer(request, "year")
        return cargo_services_service.get_services_count_by_status(
            _parse_integer(request.GET.get("status_id"), "status_id"),
            month=month,
            year=year,
        )
