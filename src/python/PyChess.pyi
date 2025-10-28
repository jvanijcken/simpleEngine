# PyChess.pyi

from typing import List, Tuple


def time_limited_iterative_deepening_search(
        pieces: list[int],
        castle_rights: list[int],
        en_passant: int,
        color: int,
        max_depth: int,
        duration_seconds: float
) -> int: ...
