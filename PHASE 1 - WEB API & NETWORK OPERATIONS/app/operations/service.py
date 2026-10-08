from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from app.audit.service import AuditService, get_audit_service
from app.operations.models import (
    DeviceOperationResult,
    DeviceOperationStatus,
    OperationResult,
    OperationStatus,
    OperationType,
)
from app.services.network_service import NetworkService


class OperationService:
    def __init__(
        self,
        network_service: NetworkService,
        max_workers: int = 3,
        audit_service: AuditService | None = None,
    ):
        self.network_service = network_service
        self.max_workers = max_workers
        self.audit_service = audit_service or get_audit_service()

    def execute(
        self,
        operation: OperationType,
        targets: list[str],
        requested_by: str = "system",
        operation_id: str | None = None,
    ) -> OperationResult:
        operation_result = OperationResult(
            operation_id=operation_id or str(uuid4()),
            operation=operation,
            status=OperationStatus.RUNNING,
            requested_by=requested_by,
            targets=targets,
            started_at=datetime.now(timezone.utc),
        )

        overall_start = perf_counter()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self._execute_device_operation,
                    operation,
                    host,
                ): host
                for host in targets
            }

            for future in as_completed(futures):
                host = futures[future]

                try:
                    result = future.result()
                except Exception as exc:
                    result = DeviceOperationResult(
                        host=host,
                        status=DeviceOperationStatus.FAILED,
                        error_type=type(exc).__name__,
                        error_message=str(exc),
                    )

                operation_result.results.append(result)

        operation_result.completed_at = datetime.now(timezone.utc)
        operation_result.duration_ms = (
            perf_counter() - overall_start
        ) * 1000

        operation_result.results.sort(
            key=lambda result: targets.index(result.host)
        )

        operation_result.finalize_status()
        self.audit_service.record_operation(operation_result)

        return operation_result

    def _execute_device_operation(
        self,
        operation: OperationType,
        host: str,
    ) -> DeviceOperationResult:
        started_at = datetime.now(timezone.utc)
        start = perf_counter()

        try:
            if operation == OperationType.COLLECT_HEALTH:
                health_result = self.network_service.get_device_health(host)
                duration_ms = (perf_counter() - start) * 1000

                if health_result.reachable:
                    return DeviceOperationResult(
                        host=host,
                        status=DeviceOperationStatus.SUCCESS,
                        started_at=started_at,
                        completed_at=datetime.now(timezone.utc),
                        duration_ms=duration_ms,
                        output=health_result.raw_output,
                    )

                return DeviceOperationResult(
                    host=host,
                    status=DeviceOperationStatus.FAILED,
                    started_at=started_at,
                    completed_at=datetime.now(timezone.utc),
                    duration_ms=duration_ms,
                    error_type="HealthCheckFailed",
                    error_message="Network device health check failed",
                )

            elif operation == OperationType.COLLECT_VERSION:
                network_result = self.network_service.execute_command(
                    host,
                    "show version",
                )

            elif operation == OperationType.COLLECT_INTERFACES:
                network_result = self.network_service.execute_command(
                    host,
                    "show ip interface brief",
                )

            elif operation == OperationType.COLLECT_ROUTES:
                network_result = self.network_service.execute_command(
                    host,
                    "show ip route",
                )

            else:
                raise ValueError(
                    f"Unsupported operation: {operation}"
                )

            duration_ms = (perf_counter() - start) * 1000

            if network_result.success:
                return DeviceOperationResult(
                    host=host,
                    status=DeviceOperationStatus.SUCCESS,
                    started_at=started_at,
                    completed_at=datetime.now(timezone.utc),
                    duration_ms=duration_ms,
                    output=network_result.output,
                )

            return DeviceOperationResult(
                host=host,
                status=DeviceOperationStatus.FAILED,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc),
                duration_ms=duration_ms,
                error_type=network_result.error_type,
                error_message=network_result.error_message,
            )

        except TimeoutError as exc:
            return DeviceOperationResult(
                host=host,
                status=DeviceOperationStatus.TIMEOUT,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc),
                duration_ms=(perf_counter() - start) * 1000,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )

        except Exception as exc:
            return DeviceOperationResult(
                host=host,
                status=DeviceOperationStatus.FAILED,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc),
                duration_ms=(perf_counter() - start) * 1000,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
