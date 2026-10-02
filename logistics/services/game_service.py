"""
logistics/services/game_service.py

Flow for every move:
  1) load the game from the DB and build the in-memory model
  2) validate in memory FIRST (cell free, game running)
  3) call the T-SQL proc; if it refuses, the model stays untouched
  4) only then mutate the model; if vs Minimax, the AI replies the same way
"""

from datastructures.game.game_model import GameModel
from datastructures.game.minimax_agent import MinimaxAgent
from logistics.services.sql_game_service import (
    sp_create_game,
    sp_make_move,
    sp_get_game,
    STATUS_OK,
    STATUS_GAME_NOT_FOUND,
    STATUS_GAME_OVER,
    STATUS_INVALID_CELL,
    STATUS_CELL_TAKEN,
    STATUS_WRONG_TURN,
)

MODES = {"human", "minimax", "ml"}


class GameNotFound(Exception):
    pass


class GameOver(Exception):
    pass


class InvalidMove(Exception):
    pass


class DatabaseError(Exception):
    pass


def _raise_for_status(status):
    if status == STATUS_OK:
        return
    if status == STATUS_GAME_NOT_FOUND:
        raise GameNotFound()
    if status == STATUS_GAME_OVER:
        raise GameOver()
    if status in (STATUS_INVALID_CELL, STATUS_CELL_TAKEN, STATUS_WRONG_TURN):
        raise InvalidMove(f"move rejected by DB (status {status})")
    raise DatabaseError(f"unexpected status {status}")


def _load(game_id):
    game = sp_get_game(game_id)
    if game is None:
        raise GameNotFound(game_id)
    return game, GameModel.from_string(game["board"])


def create_game(mode):
    if mode not in MODES:
        raise InvalidMove(f"unknown mode '{mode}'")
    return serialize_game(sp_get_game(sp_create_game(mode)))


def get_game(game_id):
    game, _ = _load(game_id)
    return serialize_game(game)


def play_move(game_id, row, column):
    game, model = _load(game_id)

    # 2) in-memory validation first
    if game["status"] != "playing":
        raise GameOver(game_id)
    if not (0 <= row < 3 and 0 <= column < 3):
        raise InvalidMove("cell out of range")
    if (row, column) not in model.get_available_moves():
        raise InvalidMove("cell already taken")

    # 3) DB decides; the model changes only if it accepts
    mark = game["turn"]
    _raise_for_status(sp_make_move(game_id, row * 3 + column, mark))
    model.make_move((row, column), mark)

    # 4) AI reply (human is X, AI is O)
    nodes_evaluated = None
    if game["mode"] == "minimax" and not model.is_game_over():
        agent = MinimaxAgent("O", "X")
        ai_move = agent.get_best_move(model)
        _raise_for_status(sp_make_move(game_id, ai_move[0] * 3 + ai_move[1], "O"))
        model.make_move(ai_move, "O")
        nodes_evaluated = agent.nodes_evaluated

    result = serialize_game(sp_get_game(game_id))
    result["nodes_evaluated"] = nodes_evaluated
    return result


def serialize_game(game):
    return {
        "id": game["id"],
        "board": [list(game["board"][i:i + 3]) for i in (0, 3, 6)],
        "turn": game["turn"],
        "mode": game["mode"],
        "status": game["status"],
    }