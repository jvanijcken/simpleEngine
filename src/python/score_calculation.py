from PyChess import direct_search
from time import perf_counter
from queue import Empty
from time import sleep
from multiprocessing import Value, Queue, Event
from multiprocessing.synchronize import Event as MPEvent


def score_worker(
        update_queue: Queue,
        task_queue:   Queue,
        shared_flag:  MPEvent):

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

            # TODO add a flag that can be observed in C

            # IMPORTANT:
            # because this function is in C and not python, this function will run in its entirety.
            # calling force_stop_calculations is no use, because there is not a moment where it can be interrupted
            score, _ = direct_search(pieces, castle_rights, en_passant, color, depth, shared_flag)


            elapsed = perf_counter() - start
            update = ("eval", (score, depth, elapsed), update_id)
            update_queue.put(update)

            depth += 1
            sleep(0.01)  # yield control, don't block too long
