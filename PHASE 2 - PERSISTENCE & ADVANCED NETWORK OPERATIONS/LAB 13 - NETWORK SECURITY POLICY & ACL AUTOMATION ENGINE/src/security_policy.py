
"""Validated security-policy models for the ACL automation engine."""

from __future__ import annotations

from enum import Enum
from ipaddress import IPv4Address, IPv4Network, ip_address, ip_network
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ACLAction(str, Enum):
    """Action applied to traffic matching a policy rule."""

    PERMIT = "permit"
    DENY = "deny"


class ACLProtocol(str, Enum):
    """Supported IPv4 ACL protocols."""

    IP = "ip"
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"


class ACLRule(BaseModel):
    """One ordered IPv4 access-control rule."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    sequence: int = Field(ge=1, le=2147483647)
    action: ACLAction
    protocol: ACLProtocol
    source: str
    destination: str
    source_port: int | None = Field(default=None, ge=1, le=65535)
    destination_port: int | None = Field(default=None, ge=1, le=65535)
    description: str = Field(default="", max_length=120)

    @field_validator("source", "destination")
    @classmethod
    def validate_ipv4_address_or_network(cls, value: str) -> str:
        """Accept IPv4 addresses or CIDR networks, rejecting IPv6."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("source and destination must not be empty")

        try:
            if "/" in value:
                network = ip_network(value, strict=False)
                if not isinstance(network, IPv4Network):
                    raise ValueError("IPv4 networks only are supported")
                return str(network)

            address = ip_address(value)
            if not isinstance(address, IPv4Address):
                raise ValueError("IPv4 addresses only are supported")
            return str(address)

        except ValueError as exc:
            raise ValueError(
                f"Invalid IPv4 address or CIDR network: {value}"
            ) from exc

    @model_validator(mode="after")
    def validate_protocol_and_ports(self) -> Self:
        """Ensure ports are only used with TCP or UDP rules."""
        if self.protocol not in (ACLProtocol.TCP, ACLProtocol.UDP):
            if self.source_port is not None or self.destination_port is not None:
                raise ValueError("Ports are supported only for TCP and UDP")

        return self


class SecurityPolicy(BaseModel):
    """A named, ordered ACL policy for a single device and interface."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    policy_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    device_id: str = Field(min_length=1, max_length=30)
    acl_name: str = Field(min_length=1, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    interface: str = Field(min_length=1, max_length=80)
    direction: str
    rules: tuple[ACLRule, ...] = Field(min_length=1, max_length=500)

    @field_validator("device_id", "interface")
    @classmethod
    def validate_nonblank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Value must not be blank")
        return value.strip()

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"in", "out"}:
            raise ValueError("direction must be 'in' or 'out'")
        return normalized

    @model_validator(mode="after")
    def validate_rule_order_and_duplicates(self) -> Self:
        """Require unique sequence numbers and reject duplicate rules."""
        sequences = [rule.sequence for rule in self.rules]
        if len(sequences) != len(set(sequences)):
            raise ValueError("Rule sequence numbers must be unique")

        normalized_rules = [
            (
                rule.action,
                rule.protocol,
                rule.source,
                rule.destination,
                rule.source_port,
                rule.destination_port,
            )
            for rule in self.rules
        ]
        if len(normalized_rules) != len(set(normalized_rules)):
            raise ValueError("Duplicate ACL rules are not allowed")

        return self


def find_rule_conflicts(policy: SecurityPolicy) -> list[str]:
    """Report exact-match traffic rules with contradictory actions.

    This conservative check does not attempt general CIDR-range overlap
    analysis. It catches rules that match the same traffic tuple but specify
    different actions.
    """
    conflicts: list[str] = []

    for index, first in enumerate(policy.rules):
        for second in policy.rules[index + 1 :]:
            same_match = (
                first.protocol == second.protocol
                and first.source == second.source
                and first.destination == second.destination
                and first.source_port == second.source_port
                and first.destination_port == second.destination_port
            )
            if same_match and first.action != second.action:
                conflicts.append(
                    f"Rules {first.sequence} and {second.sequence} match "
                    "the same traffic but have contradictory actions"
                )

    return conflicts
