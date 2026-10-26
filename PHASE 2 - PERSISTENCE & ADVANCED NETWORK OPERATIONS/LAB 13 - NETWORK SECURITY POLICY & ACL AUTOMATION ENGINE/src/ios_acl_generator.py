
"""Generate deterministic Cisco IOS extended ACL configuration."""

from __future__ import annotations

from ipaddress import IPv4Address, IPv4Network, ip_address, ip_network

from security_policy import ACLProtocol, ACLRule, SecurityPolicy


class ACLGenerationError(ValueError):
    """Raised when a policy cannot be safely represented as IOS ACL commands."""


def _ios_address(value: str) -> str:
    """Convert an IPv4 address or network into IOS ACL address syntax."""
    if value.lower() == "any":
        return "any"

    if "/" not in value:
        address = ip_address(value)
        if not isinstance(address, IPv4Address):
            raise ACLGenerationError("IPv4 addresses only are supported")
        return f"host {address}"

    network = ip_network(value, strict=False)
    if not isinstance(network, IPv4Network):
        raise ACLGenerationError("IPv4 networks only are supported")

    wildcard = IPv4Address(int(network.hostmask))
    if network.prefixlen == 32:
        return f"host {network.network_address}"
    if network.prefixlen == 0:
        return "any"

    return f"{network.network_address} {wildcard}"


def _render_rule(rule: ACLRule) -> str:
    """Render one rule as an IOS named-ACL access-list line."""
    source = _ios_address(rule.source)
    destination = _ios_address(rule.destination)

    parts = [
        " ",
        str(rule.sequence),
        rule.action.value,
        rule.protocol.value,
        source,
    ]

    if rule.source_port is not None:
        parts.extend(["eq", str(rule.source_port)])

    parts.append(destination)

    if rule.destination_port is not None:
        parts.extend(["eq", str(rule.destination_port)])

    return " ".join(part for part in parts if part)


def generate_ios_acl(policy: SecurityPolicy) -> list[str]:
    """Generate a complete named extended ACL and interface attachment.

    The returned lines are intended for review and testing first. Deployment
    should use a separate, explicitly authorized workflow.
    """
    if not policy.rules:
        raise ACLGenerationError("A policy must contain at least one rule")

    rules = sorted(policy.rules, key=lambda rule: rule.sequence)

    if len({rule.sequence for rule in rules}) != len(rules):
        raise ACLGenerationError("Rule sequence numbers must be unique")

    commands = [f"ip access-list extended {policy.acl_name}"]

    for rule in rules:
        commands.append(_render_rule(rule))

    commands.extend(
        [
            "exit",
            f"interface {policy.interface}",
            f"ip access-group {policy.acl_name} {policy.direction}",
            "exit",
        ]
    )

    return commands
