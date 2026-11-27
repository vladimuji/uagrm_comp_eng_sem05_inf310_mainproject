"""SQL Server access for payment receipts and payment summaries."""

from decimal import Decimal, InvalidOperation

from logistics.services.sql_result_service import (
    execute_single_result_set,
    execute_single_row,
)

MAX_SQL_INT = 2147483647


def _validate_positive_integer(value, parameter_name):
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
        or value > MAX_SQL_INT
    ):
        raise ValueError("{} must be a positive integer.".format(parameter_name))


def _validate_optional_positive_integer(value, parameter_name):
    if value is not None:
        _validate_positive_integer(value, parameter_name)


def list_payment_receipts(
    cargo_service_id=None,
    customer_id=None,
    payment_method=None,
    date_from=None,
    date_to=None,
):
    _validate_optional_positive_integer(cargo_service_id, "cargo_service_id")
    _validate_optional_positive_integer(customer_id, "customer_id")
    _validate_optional_positive_integer(payment_method, "payment_method")
    return execute_single_result_set(
        "EXEC dbo.sp_payment_receipt_list "
        "@cargo_service_id=%s, @customer_id=%s, @payment_method=%s, "
        "@date_from=%s, @date_to=%s",
        [
            cargo_service_id,
            customer_id,
            payment_method,
            date_from,
            date_to,
        ],
    )


def get_payment_receipt(receipt_number):
    _validate_positive_integer(receipt_number, "receipt_number")
    return execute_single_row(
        "EXEC dbo.sp_payment_receipt_get_by_id @receipt_number=%s",
        [receipt_number],
    )


def create_payment_receipt(
    cargo_service_id,
    payment_method,
    amount,
    date_time=None,
    voucher_details=None,
):
    _validate_positive_integer(cargo_service_id, "cargo_service_id")
    _validate_positive_integer(payment_method, "payment_method")

    try:
        payment_amount = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("amount must be a valid positive amount.")
    if not payment_amount.is_finite() or payment_amount <= 0:
        raise ValueError("amount must be a valid positive amount.")
    if payment_amount.as_tuple().exponent < -2 or payment_amount >= Decimal(
        "10000000000"
    ):
        raise ValueError("amount must fit DECIMAL(12, 2).")

    if voucher_details is not None:
        if not isinstance(voucher_details, str):
            raise ValueError("voucher_details must be text.")
        voucher_details = voucher_details.strip() or None
        if voucher_details is not None and len(voucher_details) > 200:
            raise ValueError("voucher_details exceeds 200 characters.")

    return execute_single_row(
        "EXEC dbo.sp_payment_receipt_create "
        "@cargo_service_id=%s, @payment_method=%s, @amount=%s, "
        "@date_time=%s, @voucher_details=%s",
        [
            cargo_service_id,
            payment_method,
            payment_amount,
            date_time,
            voucher_details,
        ],
    )


def get_payment_kpis_by_method():
    return execute_single_result_set(
        "EXEC dbo.sp_payment_get_kpis_by_method"
    )


def list_cargo_services_with_balance():
    return execute_single_result_set(
        "EXEC dbo.sp_cargo_service_list_with_balance"
    )


def get_payment_revenue_variation():
    return execute_single_row(
        "EXEC dbo.sp_payment_get_revenue_variation"
    )


def list_payment_methods():
    return execute_single_result_set("EXEC dbo.sp_payment_method_list")
