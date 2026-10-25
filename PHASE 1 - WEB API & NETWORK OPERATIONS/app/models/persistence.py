"""Persistent models for jobs, operations, audit records, and backups."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PersistentOperation(Base):
    """Durable record of a network operation."""

    __tablename__ = "network_operations"

    operation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    operation: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    requested_by: Mapped[str] = mapped_column(String(100), nullable=False)
    targets: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)

    device_results: Mapped[list["PersistentDeviceOperationResult"]] = relationship(
        back_populates="operation_record",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    job: Mapped["PersistentJob | None"] = relationship(
        back_populates="operation_record",
        uselist=False,
    )

    __table_args__ = (
        Index("ix_network_operations_created_at", "created_at"),
    )


class PersistentDeviceOperationResult(Base):
    """Durable result for one target device within an operation."""

    __tablename__ = "network_operation_device_results"

    result_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("network_operations.operation_id", ondelete="CASCADE"),
        nullable=False,
    )
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    output: Mapped[Any | None] = mapped_column(JSON)
    error_type: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)

    operation_record: Mapped[PersistentOperation] = relationship(
        back_populates="device_results"
    )

    __table_args__ = (
        Index("ix_operation_device_results_operation_id", "operation_id"),
        Index("ix_operation_device_results_host", "host"),
    )


class PersistentJob(Base):
    """Durable asynchronous job state."""

    __tablename__ = "network_jobs"

    job_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    operation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("network_operations.operation_id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)

    operation_record: Mapped[PersistentOperation | None] = relationship(
        back_populates="job"
    )

    __table_args__ = (
        Index("ix_network_jobs_created_at", "created_at"),
    )


class PersistentAuditRecord(Base):
    """Durable audit trail for completed or failed operations."""

    __tablename__ = "network_audit_records"

    audit_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("network_operations.operation_id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )
    requested_by: Mapped[str] = mapped_column(String(100), nullable=False)
    operation: Mapped[str] = mapped_column(String(50), nullable=False)
    targets: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        Index("ix_network_audit_records_created_at", "created_at"),
        Index("ix_network_audit_records_requested_by", "requested_by"),
    )


class ConfigurationBackup(Base):
    """Persistent configuration backup and its metadata."""

    __tablename__ = "network_configuration_backups"

    backup_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    device_id: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("network_devices.device_id", ondelete="RESTRICT"),
        nullable=False,
    )
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    configuration: Mapped[str] = mapped_column(Text, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    requested_by: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        Index("ix_configuration_backups_device_id", "device_id"),
        Index("ix_configuration_backups_captured_at", "captured_at"),
    )
