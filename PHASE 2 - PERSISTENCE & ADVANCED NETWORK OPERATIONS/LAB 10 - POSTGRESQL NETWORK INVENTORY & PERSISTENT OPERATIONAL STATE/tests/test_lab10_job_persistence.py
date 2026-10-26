
from unittest.mock import MagicMock, patch

from app.jobs.manager import JobManager
from app.jobs.models import JobStatus
from app.models.persistence import PersistentJob, PersistentOperation
from app.operations.models import OperationType


def test_submit_persists_job_and_operation_together():
    manager = JobManager.__new__(JobManager)
    manager.job_store = MagicMock()
    manager.executor = MagicMock()

    operation = next(iter(OperationType))
    targets = ["R1", "R2"]

    with patch("app.jobs.manager.SessionLocal.begin") as begin:
        session = begin.return_value.__enter__.return_value

        job = manager.submit(
            operation=operation,
            targets=targets,
            requested_by="lab10-test",
        )

    rows = [call.args[0] for call in session.add.call_args_list]
    operation_rows = [row for row in rows if isinstance(row, PersistentOperation)]
    job_rows = [row for row in rows if isinstance(row, PersistentJob)]

    assert len(operation_rows) == 1
    assert len(job_rows) == 1
    assert job.operation_id == operation_rows[0].operation_id
    assert job_rows[0].operation_id == operation_rows[0].operation_id
    assert operation_rows[0].targets == targets
    assert operation_rows[0].requested_by == "lab10-test"
    manager.job_store.create.assert_called_once_with(job)
    manager.executor.submit.assert_called_once()
