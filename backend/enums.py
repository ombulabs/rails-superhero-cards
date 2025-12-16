from enum import Enum


class TaskStatus(Enum):
    """Enum representing the status of a background generation task.

    Notes:
        Values are used to represent the state of a Celery task. These have been taken directly from the Celery states
        module and represent all possible states Celery can return.
    """

    #: Task state is unknown (assumed pending since you know the id).
    PENDING = (
        "PENDING",
        "pending",
        "Task state unknown, assumed pending since there is an ID.",
    )
    #: Task was received by a worker (only used in events).
    RECEIVED = ("RECEIVED", "pending", "Task was received by a worker.")
    #: Task was started by a worker (:setting:`task_track_started`).
    STARTED = ("STARTED", "started", "Task has been started by a worker.")
    #: Task succeeded
    SUCCESS = ("SUCCESS", "complete", "Task completed successfully.")
    #: Task failed
    FAILURE = ("FAILURE", "error", "Task failed with an error.")
    #: Task was revoked.
    REVOKED = ("REVOKED", "error", "Task was revoked and will not be executed.")
    #: Task was rejected (only used in events).
    REJECTED = ("REJECTED", "error", "Task was rejected by the worker.")
    #: Task is waiting for retry.
    RETRY = ("RETRY", "pending", "Task is waiting for retry.")
    IGNORED = ("IGNORED", "error", "Task was ignored and will not be executed.")

    def __new__(cls, value: str, status: str, description: str) -> "TaskStatus":
        obj = object.__new__(cls)
        obj._value_ = value
        obj.status = status
        obj.description = description
        return obj
