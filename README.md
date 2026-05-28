# Radical Enterprise

Radical Enterprise Lab is a virtualized  enterprise infrastructure environment designed to demonstrate network segmentation, identity based access, remote access VPN, DevOps, and monitoring services into a multi zone style architecture.

## Goals

The goal of the lab is to practice and demonstrate how enterprise systems integrate across networking, security, identity, and operations.

The main goals are:
- Design a realistic segmeneted enterprise network.
- Implement identity based access using Active Directory and RADIUS.
- Enforce least- privilege access between security zones.
- Deploy remote access VPN for administrative and user access.
- Integrate Linux systems with Active Directory using kerberos/SSSD.
- Deploy DevOps and monitoring services in dedicated zones.
- Practice realistic troubleshooting and operational runbooks.
- Document the environment in a way that can be reviewed, reused and improved.

## Architecture Summary

The lab follows a layered security model:

```text
Remote Users / External Access
             |
             v
     GlobalProtect VPN
             |
             v
+-----------------------------+
| Palo Alto Edge Firewall HA  |
+-----------------------------+
       |                 |
       |                 v
       |              DMZ Zone
       |
       v
  Transit Networks
       |
       v
+-----------------------------+
| Cisco Secure Firewall HA    |
| Internal Segmentation       |
+-----------------------------+
       |
       +----------+----------+----------+----------+
       |          |          |          |          |
       v          v          v          v          v
  Infra-Core   Servers     DevOps   Kubernetes  Monitoring
 AD/DNS/NPS    Apps/DB     CI/CD    Workloads   Logs/Metrics        
```

Internal zones are segmented by function and protected through firewall policy. Access between zones is explicitly allowed based on role, service dependency, and operational need.

## Technology Stack
| Area | Technologies |
|---|---|
| Network | Cisco Modeling Labs, Cisco dCloud |
| Edge Security | Palo Alto NGFW, GlobalProtect |
| Internal Security | Cisco Secure Firewall / FTD |
| Routing & Switching | OSPF, VLANs, transit networks |
| Identity | Active Directory Domain Services |
| Authentication | NPS / RADIUS, Kerberos |
| Certificates | Active Directory Certificate Services |
| Linux Integration | SSSD, Kerberos, PAM |
| DevOps | Git, Jenkins, Ansible, SonarQube, Docker |
| Containers | Kubernetes |
| Monitoring | Splunk, Grafana, Prometheus |
| Core Services | DNS, NTP, file services, mail services |

## Security Zones

| Zone | Purpose |
|---|---|
| DMZ | Externally reachable or semi-exposed services |
| Infra-Core | AD DS, DNS, DHCP, AD CS, NPS, file services |
| Servers | Internal application and database services |
| DevOps | Git, Jenkins, Ansible, SonarQube, Docker |
| Kubernetes | Container orchestration and application workloads |
| Monitoring | Splunk, Grafana, Prometheus |
| RA VPN | Remote access users connected through GlobalProtect |

## Skills Demonstrated

This lab demonstrates practical experience with:

- Enterprise network segmentation
- Firewall policy design
- Remote access VPN design
- Active Directory integration
- RADIUS/NPS authentication
- Linux domain join with SSSD/Kerberos
- DNS and certificate dependency troubleshooting
- OSPF routing and failover testing
- DevOps service placement and access control
- Monitoring and log collection design
- Operational runbooks and troubleshooting case studies

## Repository Structure

```text
radical-enterprise/
├── docs/          # Architecture, design, implementation, and troubleshooting documentation
├── diagrams/      # Logical diagrams, traffic flows, and screenshots
├── configs/       # Sanitized configuration examples
├── automation/    # CML, Ansible, and helper scripts
├── services/      # Service-specific documentation
├── policies/      # Firewall, access control, segmentation, and hardening policies
├── runbooks/      # Operational procedures
├── labs/          # Guided lab scenarios and validation exercises
└── templates/     # Reusable documentation templates
```

## Current Status

This lab is actively being built and documented.

Current focus areas:

- Baseline network segmentation
- Palo Alto edge firewall and GlobalProtect VPN
- Cisco FTD internal segmentation
- Active Directory, DNS, NPS, and certificate services
- DevOps and monitoring service deployment
- Troubleshooting case studies and operational runbooks

## Security Notice

All configurations and examples in this repository are sanitized. This repository does not include passwords, private keys, API tokens, license keys, customer data, or production configuration.

For the full security and sanitization policy, see `SECURITY.md`.

## License

This project is licensed under the MIT License.
