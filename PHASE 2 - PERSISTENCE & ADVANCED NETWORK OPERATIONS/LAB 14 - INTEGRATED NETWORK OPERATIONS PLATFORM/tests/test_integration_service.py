
from integration_service import IntegrationService


def make_service(
    *,
    fail_step=None,
    fail_rollback=False,
    audit_events=None,
):
    calls = []
    audit_events = audit_events if audit_events is not None else []

    def make_handler(step):
        def handler(context):
            calls.append(step)
            if step == fail_step:
                raise RuntimeError(f"{step} failed")
            return {"step": step, "status": "ok"}

        return handler

    def rollback(context, error):
        calls.append("rollback")
        if fail_rollback:
            raise RuntimeError("rollback failed")
        return {"status": "rolled_back"}

    def audit(event):
        audit_events.append(event)

    service = IntegrationService(
        inventory=make_handler("inventory"),
        backup=make_handler("backup"),
        configuration_deployment=make_handler(
            "configuration_deployment"
        ),
        acl_deployment=make_handler("acl_deployment"),
        verification=make_handler("verification"),
        rollback=rollback,
        audit=audit,
    )
    return service, calls, audit_events


def test_successful_workflow_runs_all_steps_and_audits():
    service, calls, events = make_service()

    result = service.execute(
        "op-001",
        {"device_id": "router-1", "actor": "admin"},
    )

    assert result.success is True
    assert result.failed_step is None
    assert result.completed_steps == [
        "inventory",
        "backup",
        "configuration_deployment",
        "acl_deployment",
        "verification",
    ]
    assert calls == result.completed_steps
    assert result.rollback_attempted is False
    assert len(events) == 1
    assert events[0]["event"] == "workflow_completed"
    assert events[0]["success"] is True


def test_inventory_failure_stops_before_deployment():
    service, calls, events = make_service(fail_step="inventory")

    result = service.execute(
        "op-002",
        {"device_id": "router-1"},
    )

    assert result.success is False
    assert result.failed_step == "inventory"
    assert result.completed_steps == []
    assert "configuration_deployment" not in calls
    assert "rollback" not in calls
    assert events[0]["event"] == "workflow_failed"


def test_deployment_failure_triggers_rollback():
    service, calls, events = make_service(
        fail_step="configuration_deployment"
    )

    result = service.execute(
        "op-003",
        {"device_id": "router-1"},
    )

    assert result.success is False
    assert result.failed_step == "configuration_deployment"
    assert result.rollback_attempted is True
    assert result.rollback_success is True
    assert calls[-1] == "rollback"
    assert events[0]["rollback_success"] is True


def test_verification_failure_triggers_rollback():
    service, calls, _ = make_service(fail_step="verification")

    result = service.execute(
        "op-004",
        {"device_id": "router-1"},
    )

    assert result.success is False
    assert result.failed_step == "verification"
    assert result.rollback_attempted is True
    assert result.rollback_success is True
    assert calls[-1] == "rollback"


def test_rollback_failure_is_reported():
    service, calls, _ = make_service(
        fail_step="configuration_deployment",
        fail_rollback=True,
    )

    result = service.execute(
        "op-005",
        {"device_id": "router-1"},
    )

    assert result.success is False
    assert result.rollback_attempted is True
    assert result.rollback_success is False
    assert "rollback_error" in result.results
    assert calls[-1] == "rollback"


def test_audit_failure_does_not_hide_workflow_result():
    service, _, _ = make_service()

    def broken_audit(event):
        raise RuntimeError("audit storage unavailable")

    service.audit_handler = broken_audit

    result = service.execute(
        "op-006",
        {"device_id": "router-1"},
    )

    assert result.success is True
    assert "audit_error" in result.results
    assert len(result.audit_events) == 1


def test_request_details_are_passed_to_handlers():
    received = []

    def inventory(context):
        received.append(context["request"])
        return {"found": True}

    service = IntegrationService(
        inventory=inventory,
        backup=lambda context: True,
        configuration_deployment=lambda context: True,
        acl_deployment=lambda context: True,
        verification=lambda context: True,
        rollback=lambda context, error: True,
        audit=lambda event: None,
    )

    request = {"device_id": "router-2", "actor": "operator"}
    result = service.execute("op-007", request)

    assert result.success is True
    assert received == [request]
