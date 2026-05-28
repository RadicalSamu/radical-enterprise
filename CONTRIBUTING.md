# Contributing

Radical Enterprise is maintained as a structured enterprise lab documentation project.

Contributions, updates, and corrections should improve the accuracy, clarity, security, or operational value of the lab.

## Documentation Standards

When adding or updating documentation, keep it clear, accurate, and practical.

Use lowercase filenames with hyphens.

Good:

```text
globalprotect-vpn.md
linux-ad-integration.md
firewall-policy-model.md
```

Avoid:

```text
GlobalProtect VPN Notes.md
LinuxADIntegration.md
final-version-2.md
```

## Document Structure

Most technical documents should follow this structure when applicable:

```markdown
# Title

## Purpose

## Scope

## Design Summary

## Components

## Configuration Notes

## Validation

## Troubleshooting Notes

## Security Considerations

## Related Documents
```

Not every document needs every section, but each document should have a clear purpose.

## Configuration Standards

Configuration examples must be sanitized before being committed.

Do not commit:

- Passwords
- API keys
- Private keys
- License keys
- Authentication tokens
- Customer data
- Production configuration
- Unsanitized firewall, VPN, or identity provider exports

Use placeholders such as:

```text
<REDACTED>
<LAB_DOMAIN>
<MGMT_IP>
<API_TOKEN>
<PRIVATE_KEY_REMOVED>
```

## Lab Scenario Standards

Each guided lab scenario should include:

- Objective
- Topology or affected zones
- Prerequisites
- Implementation steps
- Validation steps
- Troubleshooting notes
- Security considerations

## Commit Message Guidelines

Use clear commit messages that describe what changed.

Good examples:

```text
Add GlobalProtect VPN overview
Add initial security policy
Document Linux AD integration workflow
Update firewall segmentation matrix
Add OSPF failover troubleshooting case study
```

Avoid vague messages:

```text
update
fix
changes
stuff
final
```

## Review Checklist

Before committing, check that:

- The documentation is accurate.
- Markdown renders correctly.
- No secrets or sensitive values are included.
- Diagrams or screenshots do not expose sensitive data.
- File and folder names follow the repo naming style.
- Technical claims match the actual lab implementation.
