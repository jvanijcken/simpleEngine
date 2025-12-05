import time
from PyChess import direct_search
from queue import Empty
from time import sleep, time
from multiprocessing import Queue, Event, Process
from multiprocessing.synchronize import Event as MPEvent
from global_constants import Board
from move_stuff import build_move


def eval_process(waiting_task_queue: Queue, finished_task_queue: Queue, stop_flag: MPEvent):
    """ this fell is running in a separate process """

    while True:
        sleep(1 / 120)  # be idle to save calculation cost

        try: board, depth = waiting_task_queue.get_nowait()
        except Empty: continue

        print("STARTING TASK CALC")
        result = direct_search(board.pieces, board.castles, board.en_passant, board.is_white, depth, stop_flag)
        board_tuples, scores, starts, ends, alpha, calculation_interrupted, hits, misses, conflicts, writes = result

        if calculation_interrupted:
            finished_task_queue.put(None)
            print("INTERRUPTED")
            continue

        nr_of_moves = len(board_tuples)

        boards = [Board(*board_tuples[i]) for i in range(nr_of_moves)]
        moves  = [build_move(starts[i], ends[i], board, boards[i], scores[i]) for i in range(nr_of_moves)]

        result = depth, alpha, scores, boards, moves, hits, misses, conflicts, writes, time()
        finished_task_queue.put(result)
        print("RETURNED RESULT")


def init():
    waiting_task_queue  = Queue()
    finished_task_queue = Queue()
    stop_flag = Event()
    process = Process(target=eval_process, args=(waiting_task_queue, finished_task_queue, stop_flag), daemon=True)
    process.start()
    return waiting_task_queue, finished_task_queue, stop_flag, process