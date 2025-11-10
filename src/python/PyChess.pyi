# PyChess.pyi


def iterative_deepening_search(
        pieces: list[int],
        castle_rights: list[int],
        en_passant: int,
        color: int,
        max_depth: int,
        flag,
) -> tuple[list[int], list[int], int, bool, int, int, bool]: ...


def direct_search(
        pieces: list[int],
        castle_rights: list[int],
        en_passant: int,
        color: int,
        depth: int,
        flag
) -> tuple[list[int], list[int], int, bool, int, int, bool]: ...

