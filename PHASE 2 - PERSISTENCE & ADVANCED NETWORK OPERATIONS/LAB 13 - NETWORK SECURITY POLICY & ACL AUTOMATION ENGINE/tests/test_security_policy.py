
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from security_policy import (  # noqa: E402
    ACLAction,
    ACLProtocol,
    ACLRule,
    SecurityPolicy,
    find_rule_conflicts,
)
from ios_acl_generator import (  # noqa: E402
    generate_ios_acl,
)


def make_rule(
    sequence=10,
    action=ACLAction.PERMIT,
    protocol=ACLProtocol.TCP,
    source="192.0.2.0/24",
    destination="198.51.100.10",
    source_port=None,
    destination_port=443,
):
    return ACLRule(
        sequence=sequence,
        action=action,
        protocol=protocol,
        source=source,
        destination=destination,
        source_port=source_port,
        destination_port=destination_port,
    )


def make_policy(rules=None, **overrides):
    values = {
        "policy_id": "WEB-ACCESS",
        "device_id": "R1",
        "acl_name": "WEB_FILTER",
        "interface": "GigabitEthernet0/0",
        "direction": "in",
        "rules": tuple(rules or [make_rule()]),
    }
    values.update(overrides)
    return SecurityPolicy(**values)


def test_policy_accepts_valid_ipv4_cidr():
    policy = make_policy()
    assert policy.rules[0].source == "192.0.2.0/24"


def test_policy_normalizes_direction():
    policy = make_policy(direction=" OUT ")
    assert policy.direction == "out"


@pytest.mark.parametrize(
    "address",
    ["2001:db8::1", "not-an-ip", "192.0.2.999"],
)
def test_rule_rejects_invalid_or_ipv6_addresses(address):
    with pytest.raises(ValidationError):
        make_rule(source=address)


def test_rule_rejects_ports_for_icmp():
    with pytest.raises(ValidationError, match="TCP and UDP"):
        make_rule(protocol=ACLProtocol.ICMP, destination_port=443)


def test_rule_rejects_port_outside_valid_range():
    with pytest.raises(ValidationError):
        make_rule(destination_port=70000)


def test_policy_rejects_duplicate_sequence_numbers():
    with pytest.raises(ValidationError, match="sequence numbers"):
        make_policy(rules=[make_rule(10), make_rule(10, action=ACLAction.DENY)])


def test_policy_rejects_duplicate_rules():
    with pytest.raises(ValidationError, match="Duplicate ACL rules"):
        make_policy(rules=[make_rule(10), make_rule(20)])


def test_policy_rejects_invalid_direction():
    with pytest.raises(ValidationError, match="direction"):
        make_policy(direction="sideways")


def test_conflict_detection_finds_contradictory_actions():
    policy = make_policy(
        rules=[
            make_rule(10, action=ACLAction.PERMIT),
            make_rule(20, action=ACLAction.DENY),
        ]
    )

    conflicts = find_rule_conflicts(policy)
    assert len(conflicts) == 1
    assert "contradictory actions" in conflicts[0]


def test_conflict_detection_allows_same_action():
    policy = make_policy(
        rules=[
            make_rule(10, action=ACLAction.PERMIT),
            make_rule(
                20,
                action=ACLAction.PERMIT,
                destination_port=80,
            ),
        ]
    )
    assert find_rule_conflicts(policy) == []


def test_generator_sorts_rules_by_sequence():
    policy = make_policy(
        rules=[
            make_rule(20, action=ACLAction.DENY, destination_port=443),
            make_rule(10, destination_port=80),
        ]
    )

    commands = generate_ios_acl(policy)

    assert commands[0] == "ip access-list extended WEB_FILTER"
    assert commands[1].strip().startswith("10 permit tcp")
    assert commands[2].strip().startswith("20 deny tcp")


def test_generator_converts_cidr_to_wildcard_mask():
    commands = generate_ios_acl(make_policy())

    assert (
        "  10 permit tcp 192.0.2.0 0.0.0.255 "
        "host 198.51.100.10 eq 443"
    ) in commands


def test_generator_attaches_acl_to_interface():
    commands = generate_ios_acl(make_policy())

    assert "interface GigabitEthernet0/0" in commands
    assert "ip access-group WEB_FILTER in" in commands


def test_generator_supports_any_network():
    policy = make_policy(
        rules=[
            make_rule(
                source="0.0.0.0/0",
                destination="198.51.100.10",
            )
        ]
    )

    commands = generate_ios_acl(policy)
    assert "  10 permit tcp any host 198.51.100.10 eq 443" in commands


def test_generator_supports_udp():
    policy = make_policy(
        rules=[make_rule(protocol=ACLProtocol.UDP, destination_port=53)]
    )

    commands = generate_ios_acl(policy)
    assert any("permit udp" in command and "eq 53" in command for command in commands)
