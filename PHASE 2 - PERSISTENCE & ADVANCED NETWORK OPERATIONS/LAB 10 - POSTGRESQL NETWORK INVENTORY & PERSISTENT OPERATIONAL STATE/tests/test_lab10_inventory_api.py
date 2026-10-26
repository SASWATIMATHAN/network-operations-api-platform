import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.network_inventory import NetworkDevice
from app.routers.inventory import (
    create_device,
    create_interface,
    delete_device,
    get_device,
    list_devices,
    list_interfaces,
    update_device,
)
from app.schemas.inventory import DeviceCreate, DeviceUpdate, InterfaceCreate


@pytest.fixture
def db():
    """Create an isolated in-memory database for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def device_payload(
    device_id="LAB10-R1",
    hostname="LAB10-CORE-R1",
    management_ip="192.0.2.10",
):
    return DeviceCreate(
        device_id=device_id,
        hostname=hostname,
        device_type="router",
        management_ip=management_ip,
        status="active",
        description="Isolated Lab 10 test device",
    )


def test_create_and_list_inventory_devices(db):
    created = create_device(device_payload(), db)
    assert created.device_id == "LAB10-R1"
    assert created.management_ip == "192.0.2.10"

    devices = list_devices(db)
    assert any(device.device_id == "LAB10-R1" for device in devices)


def test_get_inventory_device(db):
    create_device(device_payload(), db)

    device = get_device("LAB10-R1", db)

    assert device.hostname == "LAB10-CORE-R1"


def test_get_missing_inventory_device_returns_404(db):
    with pytest.raises(HTTPException) as exc:
        get_device("MISSING-DEVICE", db)

    assert exc.value.status_code == 404


def test_update_inventory_device_persists_changes(db):
    create_device(device_payload(), db)

    payload = DeviceUpdate(
        hostname="LAB10-CORE-R1-UPDATED",
        device_type="router",
        management_ip="192.0.2.11",
        status="maintenance",
        description="Updated during Lab 10 test",
    )

    updated = update_device("LAB10-R1", payload, db)

    assert updated.hostname == "LAB10-CORE-R1-UPDATED"
    assert updated.management_ip == "192.0.2.11"
    assert updated.status == "maintenance"

    persisted = get_device("LAB10-R1", db)
    assert persisted.hostname == "LAB10-CORE-R1-UPDATED"


def test_duplicate_device_id_returns_409(db):
    create_device(device_payload(), db)

    with pytest.raises(HTTPException) as exc:
        create_device(
            device_payload(
                hostname="LAB10-OTHER-R1",
                management_ip="192.0.2.12",
            ),
            db,
        )

    assert exc.value.status_code == 409


def test_duplicate_management_ip_returns_409(db):
    create_device(device_payload(), db)

    with pytest.raises(HTTPException) as exc:
        create_device(
            device_payload(
                device_id="LAB10-R2",
                hostname="LAB10-CORE-R2",
                management_ip="192.0.2.10",
            ),
            db,
        )

    assert exc.value.status_code == 409


def test_create_and_list_device_interfaces(db):
    create_device(device_payload(), db)

    payload = InterfaceCreate(
        interface_name="GigabitEthernet0/0",
        ip_address="198.51.100.1",
        subnet_mask="255.255.255.0",
        status="up",
        description="Lab 10 test interface",
    )

    created = create_interface("LAB10-R1", payload, db)

    assert created.device_id == "LAB10-R1"
    assert created.interface_name == "GigabitEthernet0/0"

    interfaces = list_interfaces("LAB10-R1", db)
    assert len(interfaces) == 1
    assert interfaces[0].ip_address == "198.51.100.1"


def test_interface_for_missing_device_returns_404(db):
    payload = InterfaceCreate(
        interface_name="GigabitEthernet0/0",
        ip_address="198.51.100.1",
        subnet_mask="255.255.255.0",
        status="up",
        description="Missing-device test",
    )

    with pytest.raises(HTTPException) as exc:
        create_interface("MISSING-DEVICE", payload, db)

    assert exc.value.status_code == 404


def test_delete_inventory_device(db):
    create_device(device_payload(), db)

    delete_device("LAB10-R1", db)

    with pytest.raises(HTTPException) as exc:
        get_device("LAB10-R1", db)

    assert exc.value.status_code == 404


def test_update_missing_device_returns_404(db):
    payload = DeviceUpdate(
        hostname="LAB10-UNKNOWN",
        device_type="router",
        management_ip="192.0.2.13",
        status="active",
        description=None,
    )

    with pytest.raises(HTTPException) as exc:
        update_device("MISSING-DEVICE", payload, db)

    assert exc.value.status_code == 404
