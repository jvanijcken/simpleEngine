from multiprocessing import Process
from PyChess import direct_search
from time import perf_counter


def start_score_calculation(pieces, castle_rights, en_passant, color, update_queue):
    process = Process(
        target = calculate_score,
        args   = (pieces, castle_rights, en_passant, color, update_queue),
        daemon = True
    )
    process.start()


def calculate_score(pieces, castle_rights, en_passant, color, update_queue):
    start = perf_counter()
    for i in range(10):
        score, depth = direct_search(pieces, castle_rights, en_passant, color, i)
        elapsed = perf_counter() - start
        update   = ("eval", (score, depth, elapsed))
        update_queue.put(update)
        print(f"{update = }")
