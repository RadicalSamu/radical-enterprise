# Security Policy

Radical Enterprise is a simulated enterprise lab environment. This repository contains documentation, sanitized configuration examples, diagrams, automation notes, and operational runbooks.

All content must be reviewed and sanitized before being committed.

## Sensitive Information

Do not commit:

- Passwords
- API keys
- Private keys
- License keys
- Real certificates with private key material
- Authentication tokens
- Customer data
- Production configuration
- Internal company information
- Unsanitized firewall, VPN, or identity provider exports

Sensitive values should be replaced with placeholders such as:

- `<REDACTED>`
- `<LAB_DOMAIN>`
- `<MGMT_IP>`
- `<API_TOKEN>`
- `<PRIVATE_KEY_REMOVED>`
- `<LICENSE_KEY_REMOVED>`

## Configuration Examples

Configuration files in this repository are intended for educational and documentation purposes.

Before committing configuration examples, remove or replace:

- Management IP addresses that should not be public
- Public IP addresses that should not be exposed
- Usernames or service account names that should remain private
- Password hashes
- Shared secrets
- SNMP communities
- RADIUS secrets
- VPN pre-shared keys
- Certificate private keys
- Serial numbers, support IDs, or license identifiers

## Lab Scope

This repository documents a lab environment only.

Do not use these configurations directly in a production environment without proper review, testing, and adaptation to the target environment.

## Reporting Security Issues

If you notice sensitive information accidentally committed to this repository, open an issue or contact the repository owner directly.

Do not publicly disclose exposed secrets in detail inside an issue. Describe the affected file and the type of sensitive information found.
