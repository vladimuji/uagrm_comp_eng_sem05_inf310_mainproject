"""
logistics/services/sql_node_service.py

Thin wrapper around dbo.sp_insert_node / dbo.sp_delete_node /
dbo.sp_get_all_nodes. This is the "T-SQL is the source of truth"
layer INF322 wants: no ORM .create()/.delete()/.filter() calls for
nodes anymore, just EXEC + read the status code back.

tree_service.py's insert_node/delete_node should call these instead
of Node.objects.create(...) / Node.objects.filter(...).delete(),
then mutate the in-memory tree only when status == STATUS_OK.
"""

from django.db import connection

STATUS_OK = 0
STATUS_ALREADY_EXISTS = 1
STATUS_NOT_FOUND = 2


def sp_insert_node(node_id, city_name=None, state=None,
                    latitude=None, longitude=None, listed=None):
    """Returns the status code (0/1). Business-rule failures are
    represented by the status code itself, not by exceptions, so
    callers branch on an int, not a try/except.

    The @status OUTPUT param exists in the proc for T-SQL callers,
    but from Python we just read the SELECT @status AS status the
    proc also emits — far less fiddly than ODBC OUTPUT params."""
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC dbo.sp_insert_node @id=%s, @city_name=%s, @state=%s, "
            "@latitude=%s, @longitude=%s, @listed=%s",
            [node_id, city_name, state, latitude, longitude, listed],
        )
        row = cursor.fetchone()
        return row[0] if row else STATUS_OK


def sp_delete_node(node_id):
    with connection.cursor() as cursor:
        cursor.execute("EXEC dbo.sp_delete_node @id=%s", [node_id])
        row = cursor.fetchone()
        return row[0] if row else STATUS_OK


def sp_get_all_nodes():
    with connection.cursor() as cursor:
        cursor.execute("EXEC dbo.sp_get_all_nodes")
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]