from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class NetworkDevice(Base):
    """Persistent inventory record for a managed network device."""

    __tablename__ = "network_devices"

    device_id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )
    hostname: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    device_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    management_ip: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        unique=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    interfaces: Mapped[list["NetworkInterface"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index(
            "uq_network_devices_device_id_lower",
            func.lower(device_id),
            unique=True,
        ),
    )


class NetworkInterface(Base):
    """Persistent interface configuration associated with a device."""

    __tablename__ = "network_interfaces"

    device_id: Mapped[str] = mapped_column(
        String(30),
        ForeignKey(
            "network_devices.device_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    interface_name: Mapped[str] = mapped_column(
        String(80),
        primary_key=True,
    )
    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
    )
    subnet_mask: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="",
    )

    device: Mapped["NetworkDevice"] = relationship(
        back_populates="interfaces",
    )

    __table_args__ = (
        UniqueConstraint(
            "device_id",
            "interface_name",
            name="uq_network_interface_per_device",
        ),
    )
