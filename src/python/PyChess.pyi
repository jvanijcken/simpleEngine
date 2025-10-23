# PyChess.pyi

from typing import List, Tuple

class Board:
    def __init__(self, board: List[int], castles: List[int], en_passant: int, color: int) -> None: ...
    board: List[int]
    castles: List[int]
    en_passant: int
    color: int

def pyIDS(board: Board, color: int, maxDepth: int, durationSeconds: float) -> Tuple[int, List[Board]]: ...
