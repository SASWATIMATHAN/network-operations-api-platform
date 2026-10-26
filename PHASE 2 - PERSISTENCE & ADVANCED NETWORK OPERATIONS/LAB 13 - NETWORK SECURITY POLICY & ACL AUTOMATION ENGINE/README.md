# Lab 13 — Network Security Policy & ACL Automation Engine

## Objective

Implement a policy-driven network security automation engine that validates security policies, generates Cisco IOS Access Control Lists (ACLs), and deploys configuration changes through the persistent deployment workflow developed in Lab 11.

The API abstraction accepts **structured security policies rather than raw ACL commands**.

## Architecture

```text
Security Policy
      |
      v
Policy Validation
      |
      v
Conflict Detection
      |
      v
Cisco IOS ACL Generation
      |
      v
Read-Only Pre-check
      |
      v
Persistent Backup
      |
      v
Configuration Deployment
      |
      v
Post-Deployment Verification
      |
      +---- Success: Commit
      |
      +---- Failure: Rollback
                    |
                    v
             Verify Restoration
```

## Implementation

| Module | Responsibility |
|---|---|
| `src/security_policy.py` | Defines and validates security policies and ACL rules, including actions, protocols, IPv4 addresses, ports, directions, and duplicate sequences. |
| `src/ios_acl_generator.py` | Generates deterministic Cisco IOS extended ACL configuration from validated policies. |
| `src/acl_deployment_workflow.py` | Performs policy conflict checks, configuration validation, read-only pre-checks, existing ACL checks, deployment verification, and result reporting. |
| `tests/test_security_policy.py` | Tests security policy validation and rule-conflict detection. |
| `tests/test_acl_deployment_workflow.py` | Tests deployment behavior, backup handling, pre-checks, and policy rejection cases. |

## Deployment Workflow

1. Validate the requested security policy.
2. Detect contradictory rules and reject invalid policies.
3. Generate Cisco IOS extended ACL configuration.
4. Validate the generated configuration.
5. Read the current device configuration without modifying it.
6. Reject deployment if a conflicting ACL or interface binding already exists.
7. Save a persistent configuration backup through Lab 11.
8. Deploy the generated configuration.
9. Verify the resulting ACL and interface binding.
10. Commit on successful verification, or attempt rollback and verify restoration on failure.

The deployment workflow reuses Lab 11's persistent configuration deployment engine rather than implementing a separate backup and rollback system.

## Safety Considerations

- Existing ACL replacement is not enabled by default.
- Configuration validation and read-only pre-checks occur before deployment.
- Backup failure prevents deployment.
- ACL rules follow Cisco IOS first-match processing and implicit-deny behavior.
- Broad permit rules require careful review because they can weaken network security.
- Rollback outcomes are reported explicitly.

## Testing

Activate the Phase 1 virtual environment and run the Lab 13 tests:

```bash
pytest -v "$LAB13/tests"
```

**Recorded result:** 23 tests passed.

The existing Lab 11 tests additionally cover verification failure, rollback, and rollback-failure reporting.

## Scope and Limitations

- The generator targets Cisco IOS extended IPv4 ACLs.
- Policy conflict detection identifies exact-match traffic rules with contradictory actions; it does not detect every possible overlapping CIDR range.
- Existing ACL replacement is not implemented as an automatic operation.
- Passing automated tests does not establish successful deployment on a live router. Live GNS3 validation remains a separate step.

## Dependencies

- Python
- Pydantic
- Pytest
- Lab 11 configuration backup, deployment, and rollback components

## Completion Status

**Core implementation and automated tests completed.**

The lab establishes a reusable, policy-based security automation workflow with Cisco IOS ACL generation and persistent deployment safeguards.
