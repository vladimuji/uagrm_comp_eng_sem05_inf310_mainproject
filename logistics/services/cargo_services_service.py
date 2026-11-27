"""SQL Server access for cargo-service operations."""

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


def list_cargo_services(
    date_from=None,
    date_to=None,
    customer_id=None,
    driver_id=None,
    status_id=None,
    page_number=1,
    page_size=20,
):
    _validate_optional_positive_integer(customer_id, "customer_id")
    _validate_optional_positive_integer(driver_id, "driver_id")
    _validate_optional_positive_integer(status_id, "status_id")
    _validate_positive_integer(page_number, "page_number")
    _validate_positive_integer(page_size, "page_size")

    rows = execute_single_result_set(
        "EXEC dbo.sp_cargo_service_list "
        "@date_from=%s, @date_to=%s, @customer_id=%s, @driver_id=%s, "
        "@status_id=%s, @page_number=%s, @page_size=%s",
        [
            date_from,
            date_to,
            customer_id,
            driver_id,
            status_id,
            page_number,
            page_size,
        ],
    )
    return {
        "results": rows,
        "page_number": page_number,
        "page_size": page_size,
        "total_rows": rows[0]["total_rows"] if rows else None,
    }


def get_cargo_service(service_id):
    _validate_positive_integer(service_id, "service_id")
    return execute_single_row(
        "EXEC dbo.sp_cargo_service_get_by_id @service_id=%s",
        [service_id],
    )


def create_cargo_service(
    customer_id,
    zone_id,
    cargo_type_id,
    cargo_detail,
    origin,
    destination,
    date_time_scheduled,
    agreed_price,
    driver_id=None,
):
    _validate_positive_integer(customer_id, "customer_id")
    _validate_positive_integer(zone_id, "zone_id")
    _validate_positive_integer(cargo_type_id, "cargo_type_id")
    _validate_optional_positive_integer(driver_id, "driver_id")
    return execute_single_row(
        "EXEC dbo.sp_cargo_service_create "
        "@customer_id=%s, @zone_id=%s, @cargo_type_id=%s, "
        "@cargo_detail=%s, @origin=%s, @destination=%s, "
        "@date_time_scheduled=%s, @agreed_price=%s, @driver_id=%s",
        [
            customer_id,
            zone_id,
            cargo_type_id,
            cargo_detail,
            origin,
            destination,
            date_time_scheduled,
            agreed_price,
            driver_id,
        ],
    )


def update_cargo_service(
    service_id,
    cargo_detail,
    date_time_scheduled,
    agreed_price,
):
    _validate_positive_integer(service_id, "service_id")
    return execute_single_row(
        "EXEC dbo.sp_cargo_service_update "
        "@service_id=%s, @cargo_detail=%s, "
        "@date_time_scheduled=%s, @agreed_price=%s",
        [service_id, cargo_detail, date_time_scheduled, agreed_price],
    )


def assign_cargo_service_driver(service_id, driver_id):
    _validate_positive_integer(service_id, "service_id")
    _validate_positive_integer(driver_id, "driver_id")
    return execute_single_row(
        "EXEC dbo.sp_cargo_service_assign_driver "
        "@service_id=%s, @driver_id=%s",
        [service_id, driver_id],
    )


def change_cargo_service_status(service_id, new_status):
    _validate_positive_integer(service_id, "service_id")
    _validate_positive_integer(new_status, "new_status")
    return execute_single_row(
        "EXEC dbo.sp_cargo_service_change_status "
        "@service_id=%s, @new_status=%s",
        [service_id, new_status],
    )


def get_cargo_service_kpis():
    return execute_single_row("EXEC dbo.sp_cargo_service_get_kpis")


def get_unassigned_cargo_services():
    return execute_single_result_set(
        "EXEC dbo.sp_cargo_service_get_unassigned"
    )


def list_customers_simple():
    return execute_single_result_set("EXEC dbo.sp_customer_list_simple")


def list_zones_for_cargo_service():
    return execute_single_result_set("EXEC dbo.sp_zone_list")


def list_service_statuses():
    return execute_single_result_set("EXEC dbo.sp_service_status_list")


def list_available_drivers(date_time):
    if date_time is None:
        raise ValueError("date_time is required.")
    return execute_single_result_set(
        "EXEC dbo.sp_driver_list_available @date_time=%s",
        [date_time],
    )


def get_suggested_cargo_service_price(origin_node, destination_node):
    _validate_positive_integer(origin_node, "origin_node")
    _validate_positive_integer(destination_node, "destination_node")
    return execute_single_row(
        "SELECT dbo.fn_cargo_service_suggest_price(%s, %s) AS suggested_price",
        [origin_node, destination_node],
    )


def get_services_count_by_status(status_id, month=None, year=None):
    _validate_positive_integer(status_id, "status_id")
    if (month is None) != (year is None):
        raise ValueError("month and year must be supplied together.")
    if month is not None:
        _validate_positive_integer(month, "month")
        _validate_positive_integer(year, "year")
        if month > 12:
            raise ValueError("month must be between 1 and 12.")
        if year < 1753 or year > 9999:
            raise ValueError("year must be between 1753 and 9999.")
    return execute_single_row(
        "SELECT dbo.fn_get_services_count_by_status(%s, %s, %s) "
        "AS service_count",
        [status_id, month, year],
    )
