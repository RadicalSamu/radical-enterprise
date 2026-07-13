# Network Architecture

## Zones
## DMZ

**Purpose:** Hosts services that need to accept inbound access from untrusted networks.

**Members:**
- Email relay server — forwards inbound/outbound mail to the internal mail server; does not hold mailboxes
- Reverse proxy (nginx) — terminates public web traffic and forwards requests to the internal web application server; does not run the application itself

**IP Range:** 10.10.60.0/24

**Allowed in / out:**
- Communicates with the mail server and web application server in the Servers zone
- Sends logs to the Monitoring zone

**Notes / exceptions:**
- Deliberately excluded from Core-Services / domain controller access
- Gets DNS and NTP from the trusted ISP instead of internal Core-Services, to avoid depending on internal infrastructure from an untrusted-facing zone

---

## VPN Client Pool

**Purpose:** Address pool assigned to clients connecting via the Palo Alto's GlobalProtect RA VPN.

**IP Range:** 10.10.70.0/24

**Notes:**
- Static route on the Palo Alto via tunnel.1
- Redistributed into OSPF as an external route so internal zones (via the FTD) know how to return traffic to VPN clients

---

# Internal Zones

## Core-Services

**Purpose:** Provides identity, DNS, time, certificate, network access, and file services to the rest of the internal network.

**Members:**
- Domain controller — handles identity via Active Directory and DNS; the PDC emulator serves as the domain's time authority; will handle DHCP if a client network/zone is added
- NPS server — centralized network access management and accounting
- Certificate server — issues certificates for internal services (e.g., Splunk SSL certificate, Palo Alto GlobalProtect)
- Jump server — administrative access point (see notes below)
- File server — network file sharing and home directories, so user data follows them to whatever machine they log into rather than staying local to one server

**IP Range:** 10.10.10.0/24

**Allowed in / out:**
- All servers across the internal zones use this zone for DNS and identity services
- Backbone devices (Palo Alto and FTD pairs) use it for policy lookups and for the Palo Alto's RA VPN
- Servers in this zone have access to many other zones due to the services they provide
- Sends logs to the Monitoring zone

**Notes / exceptions:**
- This zone is intentionally high-trust: it concentrates identity, DNS, time, certificate issuance, and admin access in one place, so it's held to tighter access control than the other internal zones given that concentration of critical services
- **Jump server access path:** provides remote administrative access from untrusted networks via the RA VPN — direct RDP is not exposed. The VPN's Access Route setting is scoped to the jump host only, so a connected client has no route to any other internal host through the tunnel. Once connected, an admin account can RDP to the jump server; a security policy further restricts that path to the RDP protocol only
---

## DevOps Zone

**Purpose:** Hosts CI/CD tooling for the enterprise. Intended to grow into a broader DevOps practice environment (IaC, config management, etc.) as tooling is added.

**Members:** Git server, Jenkins, Ansible, SonarQube, a database (CI/CD-specific — distinct from the production application database in the Servers zone), Docker.

**IP Range:** 10.10.20.0/24

**Allowed in / out:**
- Works closely with the Kubernetes zone
- Sends logs to the Monitoring zone

---

## Kubernetes Zone

**Purpose:** Hosts the Kubernetes cluster, intended to serve as the deployment/runtime target for workloads built through the DevOps zone's CI/CD pipeline (e.g., containerized apps built and tested in DevOps, deployed here). Not yet in active use — scope and actual workflows will be defined as it's built out.

**Members:** Kubernetes server(s).

**IP Range:** 10.10.30.0/24

**Allowed in / out:**
- Works closely with the DevOps zone
- Sends logs to the Monitoring zone

---

## Servers Zone

**Purpose:** Backend services supporting the DMZ-facing applications.

**Members:**
- Internal database (production application DB — distinct from the DevOps zone's CI/CD database)
- Web application server — runs the actual application logic; only reachable via the DMZ reverse proxy, not directly internet-facing
- Mail server — holds mailboxes and user mail data; only reachable via the DMZ mail relay, not directly internet-facing

**IP Range:** 10.10.40.0/24

**Allowed in / out:**
- Works together with the servers in the DMZ zone (reverse proxy → web server, mail relay → mail server)
- Sends logs to the Monitoring zone

---

## Monitoring Zone

**Purpose:** Centralized monitoring and log analysis for the enterprise.

**Members:**
- Splunk — ingests and indexes logs/events sent from other zones
- Prometheus — ingests metrics, typically by pulling/scraping targets across zones rather than targets pushing to it
- Grafana — visualization layer only; does not ingest or store data itself, queries Splunk and Prometheus as data sources

**IP Range:** 10.10.50.0/24

**Allowed in / out:**
- Has inbound access to all zones to collect and analyze data (Prometheus pulling metrics; other zones pushing logs to Splunk)
- This is a one-way exception: other zones send/expose data to Monitoring, but do not have general access into it beyond that

## Routing

Routing in the lab is handled dynamically via OSPF.

### Perimeter — Palo Alto

The Palo Alto is the edge device, connecting to the internet via an ISP-provided IP: `198.18.1.2` (this is the dCloud IP with internet access, acting as the ISP-provided address). A static default route is configured on the Palo Alto; all outbound internet traffic is NAT/PAT'd to this IP.

The Palo Alto has:
- The default gateway interface for the DMZ
- Two interfaces connecting to the internal FTD pair

This design ensures the DMZ never reaches internal devices directly — traffic always transits the Palo Alto first, then the FTD, so it's inspected at both the perimeter and internal firewall layers.

### Perimeter-to-Internal Link (Palo Alto ↔ FTD)

Two links cross an L2 segment between the Palo Alto edge and the internal FTD pair, each on a different network with a different OSPF cost, so one is preferred and the other stays as an active, ready standby — not administratively shut down. If the primary link fails, OSPF converges to the standby immediately rather than needing to bring a downed link back up first.

Both the Palo Alto (perimeter) and the FTD (internal) are deployed in **active/passive** high availability pairs.

### OSPF Neighbor Adjacency (Palo Alto ↔ FTD)

There was no exact interface-type mapping available to form the Palo Alto–FTD OSPF neighborship directly.
- **Palo Alto (11.0):** configurable as broadcast (too permissive for a transit p2p network), point-to-point, or point-to-multipoint
- **FTD (7.7):** GUI exposes broadcast (default) or point-to-point non-broadcast

**P2P (Palo Alto) paired with P2P non-broadcast (FTD)** was adopted as the final configuration — it matches the actual topology (a genuine two-router point-to-point link) more precisely than P2MP, and avoids the overhead of maintaining a static neighbor entry. (P2MP was used initially due to an incorrect assumption that P2P wouldn't interoperate with the FTD's non-broadcast type; testing showed otherwise.)

### Internal — FTD

The FTD holds the default gateway for all internal zones and handles east-west traffic.

**Why Palo Alto handles north-south and FTD handles east-west:** this split was driven by licensing cost. As a personal lab, purchasing additional licenses is possible but not something worth spending money on, so the design works around the FTD's existing licensing limits instead — the FTD's license is renewed every 90 days by resetting the CML device and restoring from backup to retain the latest config. GlobalProtect (Palo Alto) was the only remote-access VPN option available without additional cost, and RA VPN access was needed to reach internal devices — so the Palo Alto was placed at the perimeter (to host the VPN) and the FTD was left to handle east-west traffic between internal zones.

### Management Access

Management access for both firewalls is out-of-band — a PC is directly connected to each firewall's management interface, rather than reaching them in-band through the routed network.

### FTD High-Availability Links

Two additional point-to-point subnets appear on the FTD only, distinct from the Palo Alto–FTD transit links:
- `172.16.0.12/30` — failover link
- `172.16.0.16/30` — stateful failover link

These are the HA synchronization links between the two FTD units themselves (config sync + stateful session sync), not part of the Palo Alto–FTD transit path. Worth listing separately in Transit design so they're not confused with the DMZ-side redundant links.

### Route Tables

### Palo Alto — OSPF Neighbor Adjacency

| Neighbor Address | Local Interface | Neighbor Router ID | Status | Type    |
|--------------------|-------------------|-----------------------|--------|---------|
| 172.16.0.2          | ethernet1/4 (172.16.0.1) | 111.111.111.111 | FULL   | Dynamic |
| 172.16.0.6          | ethernet1/7 (172.16.0.5) | 111.111.111.111 | FULL   | Dynamic |

### Palo Alto — OSPF Interfaces (Area 0.0.0.0)

| Interface     | Address          | Type              | Cost | Role                                        |
|-----------------|--------------------|---------------------|------|-----------------------------------------------|
| ethernet1/4      | 172.16.0.1          | Point-to-Point    | 10   | Primary link to FTD (preferred)             |
| ethernet1/7       | 172.16.0.5          | Point-to-Point    | 50   | Standby link to FTD (higher cost, always adjacent) |
| ethernet1/5       | 10.10.60.1           | Broadcast, passive | 10   | DMZ interface — advertises the DMZ subnet into OSPF but forms no adjacencies on it |

### FTD — OSPF Neighbor Adjacency

| Neighbor ID       | State | Interface     | Address     |
|--------------------|-------|----------------|-------------|
| 100.100.100.100    | FULL  | outside        | 172.16.0.1  |
| 100.100.100.100    | FULL  | 2nd-link-out   | 172.16.0.5  |

### FTD — OSPF Interfaces (Area 0)

| Interface         | Network Type      | Cost | Role                              |
|--------------------|-------------------|------|------------------------------------|
| outside             | POINT_TO_POINT    | 10   | Primary link to Palo Alto (preferred) |
| 2nd-link-out         | POINT_TO_POINT    | 50   | Standby link to Palo Alto (higher cost, always up) |
| core-services-10     | BROADCAST         | 10   | Internal zone — FTD is DR, no other OSPF routers on segment |
| devops-20            | BROADCAST         | 10   | Internal zone — FTD is DR, no other OSPF routers on segment |
| k8s-30               | BROADCAST         | 10   | Internal zone — FTD is DR, no other OSPF routers on segment |
| server-40            | BROADCAST         | 10   | Internal zone — FTD is DR, no other OSPF routers on segment |
| monitoring-50        | BROADCAST         | 10   | Internal zone — FTD is DR, no other OSPF routers on segment |

The cost difference between the primary link (10) and standby link (50) is unchanged and still implements the preferred/standby design — OSPF prefers the lower-cost path but keeps the higher-cost link fully adjacent for instant failover.
