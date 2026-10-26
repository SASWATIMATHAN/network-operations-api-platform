
from integration_service import IntegrationService


def build_service(inventory_handler):
    calls = []
    audit_events = []

    def handler(name):
        def run(context):
            calls.append(name)
            return {"status": "ok", "step": name}
        return run

    service = IntegrationService(
        inventory=inventory_handler,
        backup=handler("backup"),
        configuration_deployment=handler("configuration_deployment"),
        acl_deployment=handler("acl_deployment"),
        verification=handler("verification"),
        rollback=lambda context, error: calls.append("rollback") or True,
        audit=lambda event: audit_events.append(event),
    )
    return service, calls, audit_events


def test_inventory_exception_stops_workflow():
    def unavailable_inventory(context):
        raise RuntimeError("PostgreSQL unavailable")

    service, calls, events = build_service(unavailable_inventory)

    result = service.execute(
        "inventory-safety-001",
        {"device_id": "R1"},
    )

    assert result.success is False
    assert result.failed_step == "inventory"
    assert result.completed_steps == []
    assert calls == []
    assert result.rollback_attempted is False
    assert events[0]["event"] == "workflow_failed"


def test_inventory_false_result_stops_workflow():
    service, calls, events = build_service(
        lambda context: False
    )

    result = service.execute(
        "inventory-safety-002",
        {"device_id": "R1"},
    )

    assert result.success is False
    assert result.failed_step == "inventory"
    assert result.completed_steps == []
    assert calls == []
    assert result.rollback_attempted is False
    assert events[0]["success"] is False


def test_inventory_none_result_stops_workflow():
    service, calls, _ = build_service(
        lambda context: None
    )

    result = service.execute(
        "inventory-safety-003",
        {"device_id": "R1"},
    )

    assert result.success is False
    assert result.failed_step == "inventory"
    assert result.completed_steps == []
    assert calls == []
