from PyChess import direct_search
from queue import Empty
from time import sleep
from multiprocessing import Queue
from multiprocessing.synchronize import Event as MPEvent
from multiprocessing import Event, Process
from globals import Board, MPTask, MPResult
from threading import Lock
from dataclasses import dataclass



class MPWorker:
    def __init__(self):
        self._waiting_task_queue  = Queue()
        self._finished_task_queue = Queue()
        self._stop_flag           = Event()

        self._process = Process(
            target = mp_worker,
            args   = (self._waiting_task_queue, self._finished_task_queue, self._stop_flag),
            daemon = True
        )
        self._process.start()
        self._ongoing_tasks = 0

    def is_idle(self) -> bool:
        return self._ongoing_tasks == 0

    def add_task(self, board, depth, update_id) -> None:
        self._stop_flag.clear()
        task = MPTask(
            board.pieces, board.castles, board.en_passant, board.is_white, depth, update_id
        )
        self._ongoing_tasks += 1
        print(f"{self._ongoing_tasks = }")
        self._waiting_task_queue.put(task)

    def terminate_all_tasks(self):
        while True:
            try:
                self._waiting_task_queue.get_nowait()
            except Empty:
                break
        self._stop_flag.set()


    def get_next_result(self) -> None | MPResult:
        try:
            task = self._finished_task_queue.get_nowait()
        except Empty:
            return None

        self._ongoing_tasks -= 1
        print(f"{self._ongoing_tasks = }")
        return task


def mp_worker(
        waiting_task_queue:  Queue,
        finished_task_queue: Queue,
        stop_flag:           MPEvent):

    current_task: MPTask | None = None

    while True:
        try:  # check for new task
            current_task: MPTask = waiting_task_queue.get_nowait()
        except Empty: ...

        if current_task:
            result = direct_search(
                current_task.pieces,
                current_task.castles,
                current_task.en_passant,
                current_task.is_white,
                current_task.start_depth,
                stop_flag
            )
            result = MPResult(*result, update_id=current_task.update_id)
            finished_task_queue.put(result)
        sleep(0.1)  # yield control, don't block too long

