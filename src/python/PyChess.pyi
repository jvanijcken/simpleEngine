# PyChess.pyi

from typing import List, Tuple


def iterative_deepening_search(
        pieces: list[int],
        castle_rights: list[int],
        en_passant: int,
        color: int,
        max_depth: int,
) -> tuple[int, int]: ...


def direct_search(
        pieces: list[int],
        castle_rights: list[int],
        en_passant: int,
        color: int,
        depth: int,
        flag
) -> tuple[int, int]: ...


def force_stop_calculations() -> None: ...
