from .worker import WorkerCBF, blocking_scheduler, get_connection

from functools import partial

__all__ = ["WorkerCBF", "blocking_scheduler", "init_app"]


def init_app(host, port, virtual_host, user, password, qtd_consumers):
    connection = get_connection(host, port, virtual_host, user, password)
    worker = WorkerCBF(connection, qtd_consumers=qtd_consumers)
    blocking_scheduler.add_job(
        worker.heartbeat,
        trigger="interval",
        seconds=60 * 5,
    )
    return partial(start, worker=worker)


def start(now=False, worker=None):
    if now:
        worker.heartbeat()
    blocking_scheduler.start()
