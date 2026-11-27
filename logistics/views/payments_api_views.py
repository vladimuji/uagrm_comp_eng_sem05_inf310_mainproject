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

from logistics.services import payments_service
from logistics.services.sql_result_service import SqlResultShapeError

logger = logging.getLogger(__name__)

PAYMENT_ERROR_STATUSES = {
    51029: 400,
    51030: 404,
    51031: 400,
    51032: 400,
    51033: 404,
    51034: 409,
    51035: 409,
    51036: 409,
}


def _parse_sql_business_error(error):
    error_text = " ".join(str(argument) for argument in error.args)
    match = re.search(r"\((510\d{2})\)", error_text)
    if match is None:
        return None

    error_code = int(match.group(1))
    status_code = PAYMENT_ERROR_STATUSES.get(error_code)
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


def _parse_positive_integer(value, name):
    if isinstance(value, bool):
        raise ValueError("{} must be a positive integer.".format(name))
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError("{} must be a positive integer.".format(name))
    if (
        parsed <= 0
        or parsed > payments_service.MAX_SQL_INT
        or str(parsed) != str(value).strip()
    ):
        raise ValueError("{} must be a positive integer.".format(name))
    return parsed


def _parse_optional_query_integer(request, name):
    raw_value = request.GET.get(name)
    if raw_value in (None, ""):
        return None
    return _parse_positive_integer(raw_value, name)


def _parse_date_query(request, name):
    raw_value = request.GET.get(name)
    if raw_value in (None, ""):
        return None
    value = parse_date(raw_value)
    if value is None:
        raise ValueError("'{}' must be an ISO date.".format(name))
    return value


def _parse_datetime(value, name):
    parsed = parse_datetime(value) if isinstance(value, str) else None
    if parsed is None:
        raise ValueError("'{}' must be an ISO date and time.".format(name))
    if timezone.is_aware(parsed):
        parsed = timezone.make_naive(parsed, datetime_timezone.utc)
    return parsed


def _request_payload(request):
    try:
        payload = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Request body must contain valid JSON.")
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")
    return payload


def _parse_amount(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("'amount' must be a valid positive amount.")
    if not amount.is_finite() or amount <= 0:
        raise ValueError("'amount' must be a valid positive amount.")
    if amount.as_tuple().exponent < -2 or amount >= Decimal("10000000000"):
        raise ValueError("'amount' must fit DECIMAL(12, 2).")
    return amount


def _business_error_response(error):
    business_error = _parse_sql_business_error(error)
    if business_error is None:
        logger.exception("Payment SQL operation failed")
        return JsonResponse(
            {"error": "Payment operation could not be completed"},
            status=500,
        )

    error_code, status_code, message = business_error
    logger.warning("Payment operation rejected by SQL rule %s", error_code)
    return JsonResponse(
        {"error": message, "code": error_code},
        status=status_code,
    )


class PaymentsApiView(View):
    post_status = 200

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        return super().dispatch(request, *args, **kwargs)

    def get_data(self, request, **kwargs):
        raise NotImplementedError

    def post_data(self, request, payload, **kwargs):
        raise NotImplementedError

    def _respond(self, callback, status=200):
        try:
            return JsonResponse(callback(), safe=False, status=status)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)
        except SqlResultShapeError:
            logger.exception("Payment SQL result had an unexpected shape")
            return JsonResponse(
                {"error": "Payment data could not be loaded"},
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


class PaymentReceiptListCreateApiView(PaymentsApiView):
    post_status = 201

    def get_data(self, request):
        return payments_service.list_payment_receipts(
            cargo_service_id=_parse_optional_query_integer(
                request, "cargo_service_id"
            ),
            customer_id=_parse_optional_query_integer(request, "customer_id"),
            payment_method=_parse_optional_query_integer(
                request, "payment_method"
            ),
            date_from=_parse_date_query(request, "date_from"),
            date_to=_parse_date_query(request, "date_to"),
        )

    def post_data(self, request, payload):
        raw_date_time = payload.get("date_time")
        date_time = (
            _parse_datetime(raw_date_time, "date_time")
            if raw_date_time not in (None, "")
            else None
        )
        voucher_details = payload.get("voucher_details")
        if voucher_details is not None and not isinstance(voucher_details, str):
            raise ValueError("'voucher_details' must be text.")

        return payments_service.create_payment_receipt(
            cargo_service_id=_parse_positive_integer(
                payload.get("cargo_service_id"),
                "cargo_service_id",
            ),
            payment_method=_parse_positive_integer(
                payload.get("payment_method"),
                "payment_method",
            ),
            amount=_parse_amount(payload.get("amount")),
            date_time=date_time,
            voucher_details=voucher_details,
        )


class PaymentReceiptDetailApiView(PaymentsApiView):
    def get_data(self, request, receipt_number):
        return payments_service.get_payment_receipt(receipt_number)


class PaymentKpisByMethodApiView(PaymentsApiView):
    def get_data(self, request):
        return payments_service.get_payment_kpis_by_method()


class CargoServicesWithBalanceApiView(PaymentsApiView):
    def get_data(self, request):
        return payments_service.list_cargo_services_with_balance()


class PaymentRevenueVariationApiView(PaymentsApiView):
    def get_data(self, request):
        return payments_service.get_payment_revenue_variation()


class PaymentMethodsForReceiptApiView(PaymentsApiView):
    def get_data(self, request):
        return payments_service.list_payment_methods()
