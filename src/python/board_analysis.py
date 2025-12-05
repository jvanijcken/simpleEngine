from queue import Empty
from time import sleep
from multiprocessing import Event, Process
from threading import Thread, Lock
from background_process import eval_process
from queue import Queue

from background_process import init


WAITING_TASK_QUEUE, FINISHED_TASK_QUEUE, STOP_FLAG, PROCESS = init()

ARGS_FOR_BACKGROUND_THREAD = Queue()
LOCK = Lock()


def evaluate(queue, board, depth) -> bool:
    if LOCK.acquire(blocking=False):
        try:
            if ARGS_FOR_BACKGROUND_THREAD.empty():
                ARGS_FOR_BACKGROUND_THREAD.put((queue, board, depth))
        finally:  # in case we get some error in our code above
            LOCK.release()
            return True  # let's just assume this was successful
    return False



def background_thread():
    while True:
        sleep(1 / 120)

        with LOCK:

            try: queue, board, depth = ARGS_FOR_BACKGROUND_THREAD.get_nowait()
            except Empty: continue

            print("I GOT A TASK!")
            STOP_FLAG.clear()
            WAITING_TASK_QUEUE.put((board, depth))
            result = FINISHED_TASK_QUEUE.get()
            print(f"I GOT A RESULT!")
            queue.put(result)


THREAD_2 = Thread(target=background_thread, daemon=True)
THREAD_2.start()


def stop_background_eval_calculation():
    """ this function terminates ongoing calculations """
    print("ABORT!")
    STOP_FLAG.set()

