from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.network_inventory import NetworkDevice, NetworkInterface
from app.schemas.inventory import (
    DeviceCreate,
    DeviceResponse,
    DeviceUpdate,
    InterfaceCreate,
    InterfaceResponse,
)

router = APIRouter(prefix="/inventory", tags=["Persistent Inventory"])


@router.post(
    "/devices",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
):
    device = NetworkDevice(
        device_id=payload.device_id,
        hostname=payload.hostname,
        device_type=payload.device_type,
        management_ip=str(payload.management_ip),
        status=payload.status,
        description=payload.description,
    )
    db.add(device)
    try:
        db.commit()
        db.refresh(device)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device ID or management IP already exists.",
        ) from exc
    return device


@router.get("/devices", response_model=list[DeviceResponse])
def list_devices(db: Session = Depends(get_db)):
    return db.scalars(
        select(NetworkDevice).order_by(NetworkDevice.device_id)
    ).all()


@router.get("/devices/{device_id}", response_model=DeviceResponse)
def get_device(device_id: str, db: Session = Depends(get_db)):
    device = db.get(NetworkDevice, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found.")
    return device


@router.put("/devices/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: str,
    payload: DeviceUpdate,
    db: Session = Depends(get_db),
):
    device = db.get(NetworkDevice, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found.")

    device.hostname = payload.hostname
    device.device_type = payload.device_type
    device.management_ip = str(payload.management_ip)
    device.status = payload.status
    device.description = payload.description

    try:
        db.commit()
        db.refresh(device)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Management IP already belongs to another device.",
        ) from exc
    return device


@router.delete(
    "/devices/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_device(device_id: str, db: Session = Depends(get_db)):
    device = db.get(NetworkDevice, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found.")

    db.delete(device)
    db.commit()


@router.post(
    "/devices/{device_id}/interfaces",
    response_model=InterfaceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interface(
    device_id: str,
    payload: InterfaceCreate,
    db: Session = Depends(get_db),
):
    if db.get(NetworkDevice, device_id) is None:
        raise HTTPException(status_code=404, detail="Device not found.")

    interface = NetworkInterface(
        device_id=device_id,
        interface_name=payload.interface_name,
        ip_address=str(payload.ip_address),
        subnet_mask=payload.subnet_mask,
        status=payload.status,
        description=payload.description,
    )
    db.add(interface)
    try:
        db.commit()
        db.refresh(interface)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Interface already exists for this device.",
        ) from exc
    return interface


@router.get(
    "/devices/{device_id}/interfaces",
    response_model=list[InterfaceResponse],
)
def list_interfaces(device_id: str, db: Session = Depends(get_db)):
    if db.get(NetworkDevice, device_id) is None:
        raise HTTPException(status_code=404, detail="Device not found.")

    return db.scalars(
        select(NetworkInterface)
        .where(NetworkInterface.device_id == device_id)
        .order_by(NetworkInterface.interface_name)
    ).all()
