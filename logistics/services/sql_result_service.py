"""Shared execution and result mapping for SQL Server queries."""

from django.db import connection


class SqlResultShapeError(RuntimeError):
    """Raised when SQL returns an unexpected number of result sets or rows."""


def read_result_sets(cursor):
    result_sets = []
    while True:
        if cursor.description is not None:
            columns = [column[0] for column in cursor.description]
            result_sets.append([
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ])

        nextset = getattr(cursor, "nextset", None)
        if nextset is None or not nextset():
            break

    return result_sets


def execute_result_sets(sql, params=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        return read_result_sets(cursor)


def execute_single_result_set(sql, params=None):
    result_sets = execute_result_sets(sql, params)
    if len(result_sets) != 1:
        raise SqlResultShapeError(
            "Expected one tabular result set; received {}.".format(
                len(result_sets)
            )
        )
    return result_sets[0]


def execute_single_row(sql, params=None):
    rows = execute_single_result_set(sql, params)
    if len(rows) != 1:
        raise SqlResultShapeError(
            "Expected one row; received {}.".format(len(rows))
        )
    return rows[0]
