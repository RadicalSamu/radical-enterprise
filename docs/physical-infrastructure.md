# Physical Architecture

## Design Philosophy

The hardware specifications below reflect what's currently used for the full Radical Enterprise lab. The [`labs`](../labs/) section of the repo is meant to break this down into smaller, standalone versions, so it's possible to follow along with the same technologies and configurations, but scaled to bare-minimum requirements — each smaller lab is effectively a puzzle piece of how to implement the same setup without needing hardware anywhere close to what's listed here.

These specifications are also expected to shrink over time. As telemetry accumulates on actual resource usage, the plan is to right-size each component — giving it only what it needs to run optimally, once real usage patterns make that apparent, rather than over-provisioning up front.

## Inside CML

| Component              | Count | vCPUs | RAM   |
|--------------------------|-------|-------|-------|
| Layer 2 switches          | 7     | 1     | 1 GB  |
| FTD firewalls              | 2     | 4     | 8 GB  |
| Palo Alto firewalls        | 2     | 4     | 8 GB  |
| External connectors        | 8     | —     | —     |

**External connectors:** technically only one connector would be needed to reach the dCloud platform, but one connector per zone was used instead to keep the topology visually cleaner. This doesn't meaningfully affect resource usage and doesn't count against the 20-node CML license.

## Inside dCloud

| Component                    | Count | vCPUs | RAM    | Storage | Notes                                  |
|--------------------------------|-------|-------|--------|---------|------------------------------------------|
| CML host node                   | 1     | 16    | 64 GB  | 371 GB  | Hosts the CML backbone/topology above  |
| Linux VMs (Ubuntu/Alma)          | 13    | 4     | 8 GB   | 70 GB   | General-purpose Linux systems           |
| Splunk VM                         | 1     | 4     | 12 GB  | 70 GB   |                                            |
| Grafana VM                         | 1     | 2     | 4 GB   | 70 GB   |                                            |
| Windows servers (general)          | 2     | 2     | 4 GB   | 99 GB   |                                            |
| Windows server (file server)        | 1     | 4     | 8 GB   | 99 GB   |                                            |
| Windows server (domain controller)   | 1     | 2     | 4 GB   | 99 GB   |                                            |
| Windows PCs                          | 2     | 8     | 16 GB  | 80 GB   |                                            |

## Notes

- **Outside PC:** one of the two Windows PCs is intentionally kept outside the CML-routed topology, living directly in dCloud — this represents an external/untrusted-network client for testing access into the lab (e.g., RA VPN, DMZ-facing services) without being part of the internal routed network itself.
