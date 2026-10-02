"""
logistics/services/sql_game_service.py

Thin wrapper around dbo.sp_create_game / sp_make_move / sp_get_game.
Business-rule failures come back as status codes, not exceptions.
"""

from django.db import connection

STATUS_OK = 0
STATUS_GAME_NOT_FOUND = 1
STATUS_GAME_OVER = 2
STATUS_INVALID_CELL = 3
STATUS_CELL_TAKEN = 4
STATUS_WRONG_TURN = 5


def sp_create_game(mode):
    """Returns the new game id."""
    with connection.cursor() as cursor:
        cursor.execute(
            "DECLARE @s INT; "
            "EXEC dbo.sp_create_game @mode=%s, @status=@s OUTPUT;",
            [mode],
        )
        row = cursor.fetchone()
        return row[1]


def sp_make_move(game_id, cell, mark):
    """Returns the status code (0..5)."""
    with connection.cursor() as cursor:
        cursor.execute(
            "DECLARE @s INT; "
            "EXEC dbo.sp_make_move @game_id=%s, @cell=%s, @mark=%s, "
            "@status=@s OUTPUT;",
            [game_id, cell, mark],
        )
        row = cursor.fetchone()
        return row[0] if row else STATUS_OK


def sp_get_game(game_id):
    """Returns a dict, or None if the game does not exist."""
    with connection.cursor() as cursor:
        cursor.execute("EXEC dbo.sp_get_game @game_id=%s", [game_id])
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))