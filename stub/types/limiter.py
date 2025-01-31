import threading
from typing import List, Callable

__all__ = ["Limiter"]


class Limiter:
    """
    Implementation of a thread limiter that ensures only max_threads threads are running at a time.
    """

    def __init__(self, max_threads: int) -> None:
        self.max_threads = max_threads
        self.lock = threading.Lock()
        self.semaphore = threading.Semaphore(max_threads)

        self._active_threads: List[threading.Thread] = []
        self._total_threads: int = 0

    @property
    def active_threads(self) -> List[threading.Thread]:
        return self._active_threads

    @property
    def total_threads(self) -> int:
        return self._total_threads

    def _worker(self, task: Callable, *args, **kwargs) -> None:
        """
        Worker method to execute the task with given arguments.
        """
        try:
            task(*args, **kwargs)
        finally:
            with self.lock:
                self._active_threads.remove(threading.current_thread())
            self.semaphore.release()

    def add_task(self, task: Callable, *args, **kwargs) -> None:
        """
        Add a task to be executed
        """
        with self.lock:
            self._total_threads += 1

        self.semaphore.acquire()

        thread = threading.Thread(
            target=self._worker,
            args=(
                task,
                *args,
            ),
            kwargs=kwargs,
        )
        with self.lock:
            self._active_threads.append(thread)
        thread.start()

    def close(self) -> None:
        """
        Close the limiter, waiting for all threads to finish their tasks.
        """
        for thread in self.active_threads:
            thread.join()

        with self.lock:
            self._active_threads.clear()
            self._total_threads = 0

    reset = close
