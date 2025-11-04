from PyChess import direct_search
from time import perf_counter
from queue import Empty
from time import sleep
from multiprocessing import Queue
from multiprocessing.synchronize import Event as MPEvent
from globals import Board


def score_worker(
        update_queue: Queue,
        task_queue:   Queue,
        shared_flag:  MPEvent):

    current_task = None
    depth = 0

    while True:
        print("looping...")
        # check for new task
        try:
            new_task = task_queue.get_nowait()
            if new_task == "STOP":
                break
            current_task = new_task
            depth = 0
            shared_flag.clear()  # set value to false
        except Empty:
            pass


        if current_task:
            pieces, castle_rights, en_passant, color, update_id = current_task

            start = perf_counter()

            print("start calculation...")
            score, _depth, pieces, castle, en_passant, color = direct_search(pieces, castle_rights, en_passant, color, depth, shared_flag)
            print("end calculation")


            elapsed = perf_counter() - start
            update = ("eval", (score, depth, elapsed), update_id)
            update_queue.put(update)

            depth += 1
            sleep(0.01)  # yield control, don't block too long



def move_worker(
        update_queue: Queue,
        task_queue:   Queue,
        shared_flag: MPEvent):

    current_task = None
    depth = 0

    while True:
        # check for new task
        try:
            new_task = task_queue.get_nowait()
            if new_task == "STOP":
                break
            current_task = new_task
            depth = 0
            shared_flag.clear()  # set value to false
        except Empty:
            pass


        if current_task:
            pieces, castle_rights, en_passant, color, update_id = current_task

            start = perf_counter()

            score, _depth, pieces, castle, en_passant, color = direct_search(pieces, castle_rights, en_passant, color, depth, shared_flag)

            best_position = Board(
                pieces     = pieces,
                castles    = castle,
                en_passant = en_passant,
                is_white   = color == 0
            )

            elapsed = perf_counter() - start
            update = ("best_position", best_position, update_id)
            update_queue.put(update)

            depth += 1
            sleep(0.01)  # yield control, don't block too long

