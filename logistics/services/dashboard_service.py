"""SQL Server access for the dashboard's database-backed datasets."""

from logistics.services.sql_result_service import (
    SqlResultShapeError as DashboardResultShapeError,
    execute_result_sets as _execute_result_sets,
    execute_single_result_set as _execute_single_result_set,
    execute_single_row as _execute_single_row,
    read_result_sets as _read_result_sets,
)


def _validate_positive_integer(value, parameter_name):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError("{} must be a positive integer.".format(parameter_name))


def get_dashboard_kpis():
    kpis = _execute_single_row("EXEC dbo.sp_dashboard_get_kpis")
    rates = _execute_single_row(
        "DECLARE @now DATETIME2(7) = SYSUTCDATETIME(); "
        "SELECT "
        "dbo.fn_get_monthly_collection_rate(MONTH(@now), YEAR(@now)) "
        "AS monthly_collection_rate, "
        "dbo.fn_get_service_count_variation() AS service_count_variation"
    )
    return {
        "kpis": kpis,
        "monthly_collection_rate": rates["monthly_collection_rate"],
        "service_count_variation": rates["service_count_variation"],
    }


def get_fleet_availability():
    return _execute_single_row(
        "SELECT en_ruta, total, porcentaje "
        "FROM dbo.fn_get_fleet_availability_ratio()"
    )


def get_pending_balances():
    return _execute_single_row("EXEC dbo.sp_dashboard_get_pending_balances")


def get_revenue_by_month(months=6):
    _validate_positive_integer(months, "months")
    return _execute_single_result_set(
        "EXEC dbo.sp_dashboard_get_revenue_by_month @months=%s",
        [months],
    )


def get_services_by_type():
    return _execute_single_result_set(
        "EXEC dbo.sp_dashboard_get_services_by_type"
    )


def get_recent_services(top_n=5):
    _validate_positive_integer(top_n, "top_n")
    return _execute_single_result_set(
        "EXEC dbo.sp_dashboard_get_recent_services @top_n=%s",
        [top_n],
    )
