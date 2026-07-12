# tz-cr-task

## Purpose
Configures Windows systems to use the Costa Rica timezone and maintain consistent time synchronization.

## Configuration

- Timezone:
  - Central America Standard Time (UTC-06:00)

- Time synchronization:
  - Uses Active Directory domain hierarchy
  - Disables Hyper-V VM time provider to prevent host time overrides
  - Forces time rediscovery and resynchronization

## Scope

Applied to:

- REL → Computers → Windows OU

## Validation

Verified using:

    gpresult /scope computer /r

Applied GPO:

    tz-cr-task
