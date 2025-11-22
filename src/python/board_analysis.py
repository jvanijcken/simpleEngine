import time
import sys
print(sys.path)
from PyChess import direct_search
from queue import Empty
from time import sleep, time
from multiprocessing import Queue
from multiprocessing.synchronize import Event as MPEvent
from multiprocessing import Event, Process
from global_constants import Board, MPTask, MPResult, BoardAnalysis
from threading import Thread, Lock, current_thread, main_thread

# TODO c code does not terminate when flag is set


class MPWorker:
    def __init__(self):
        self._waiting_task_queue  = Queue()
        self._finished_task_queue = Queue()
        self._stop_flag           = Event()

        _process = Process(
            target = mp_process,
            args   = (
                self._waiting_task_queue,
                self._finished_task_queue,
                self._stop_flag),
            daemon = True
        )
        _process.start()

    def evaluate(self, board, depth, identity) -> dict[int, BoardAnalysis] | None:
        """ this function is blocking for as long as the calculation takes """
        task = MPTask(board, depth, identity)
        self._waiting_task_queue.put(task)
        return self._finished_task_queue.get()

    def abort(self, blocking=False):
        """ this function terminates ongoing calculations """
        self._stop_flag.set()

        if not blocking:
            return

        while True:
            if ...:
                return
            sleep(1 / 120)

    def initiate(self):
        """ this function makes sure calculations aren't terminated anymore """
        self._stop_flag.clear()


def mp_process(
        waiting_task_queue:  Queue,
        finished_task_queue: Queue,
        stop_flag:           MPEvent):

    while True:
        sleep(1 / 120)  # be idle to save calculation cost
        try:  # check for new task
            current_task: MPTask = waiting_task_queue.get_nowait()
            result = direct_search(
                current_task.board.pieces,
                current_task.board.castles,
                current_task.board.en_passant,
                current_task.board.is_white,
                current_task.start_depth,
                stop_flag
                )
            _moves, scores, alpha, calculation_interrupted, hits, misses, conflicts, writes = result
            moves = [Board(*x) for x in _moves]

            if calculation_interrupted:
                finished_task_queue.put(None)
                continue

            result = dict()
            result[current_task.start_depth] = BoardAnalysis(
                best_score              = alpha           ,
                scores                  = scores          ,
                moves                   = moves           ,
                hits                    = hits            ,
                misses                  = misses          ,
                conflicts               = conflicts       ,
                writes                  = writes          ,
                update_id               = current_task.update_id,
                time_of_last_update     = time()
            )
            finished_task_queue.put(result)

        except Empty:
            continue


class Scheduler:
    def __init__(self):
        self._function_queue  = Queue()
        self._worker = Thread(
            target=scheduler_thread,
            args=(self._function_queue, self._lock, self._unlock),
            daemon=True
        )
        self._worker.start()
        self._locked = False
        self._lock = Lock()

    def _lock(self):
        """ used by my thread to signal it is busy with a task """
        with self._lock:
            self._locked = True

    def _unlock(self):
        """ used by my thread to signal it is finished with its task and can receive a new task """
        with self._lock:
            self._locked = False

    def __call__(self, function):
        """ add a new task for worker, will raise ValueError if worker is occupied """
        assert (current_thread() == main_thread())

        with self._lock:
            if not self._function_queue.empty():  # some task is waiting already
                raise ValueError("another task waiting, wait until worker is finished with previous task")
            if self._locked:                      # worker is busy
                raise ValueError("worker busy, wait until worker is finished with previous task")

        self._function_queue.put(function)

    def wait_after_task_finished(self):
        """ blocks until worker isn't busy anymore """
        while True:
            sleep(1 / 120)
            if not self._locked:
                break


def scheduler_thread(function_queue: Queue, lock, unlock):
    while True:
        sleep(1 / 120)

        # work on a task
        lock()
        try:
            function = function_queue.get_nowait()
            function()
        except Empty:
            ...
        unlock()
