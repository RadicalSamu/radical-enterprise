# Admin Roles

> **Note:** The personas below were created partly for fun, but they serve a real purpose — each one exists to keep scope and responsibility separate and clearly defined. This doc is meant to act as a guide when building out group-based permissions, NPS policies, GPOs, and access boundaries later. Think of it as an early sketch of role-based access control (RBAC), written in a way that's actually easy to remember.

## Summary

| Name              | OU                  | Role                          | Access Scope                                                        |
|--------------------|----------------------|----------------------------------|-------------------------------------------------------------------------|
| Kusanagi Motoko (The Major) | `00-Major`           | Overseer / Owner-level access    | Full — every zone, every device, no restriction                        |
| Cyborg              | `Users/admins`        | Core-Services zone administrator | Core-Services: DC, file server, NPS, certificate services              |
| Mr. Robot            | `Users/admins`        | Security engineer                 | Monitoring zone, Palo Alto, FTD pair, NPS, certificate services (shared) |
| J.A.R.V.I.S.          | `Users/service-accounts` or `Users/admins` (tbd) | Mail infrastructure | Mail server (Servers zone), mail relay (DMZ)                          |
| Tecna Zenith           | `Users/admins`        | Kubernetes zone administrator     | Kubernetes zone; shared access to web app server for site deployment  |
| Ada Lovelace             | `Users/admins`        | DevOps zone administrator          | DevOps zone; shared access to web app server for site deployment      |

---

## Kusanagi Motoko (The Major)

**OU:** `00-Major`
**Role:** Overseer / Owner-level access
**Access scope:** Full — every zone, every device, no restriction

### Lore

Publicly, no one at Radical Enterprise reports to "The Major" — because officially, she isn't staff. She's the account that exists in case every other account, every other admin, every other layer of trust fails at once. The ghost in this particular shell isn't tied to any one department, any one zone, any one piece of hardware. She doesn't need delegated access because there's nothing to delegate — she *is* the root of trust the rest of the org chart hangs off of.

Day to day, this account does nothing. It's not meant to be convenient, and it's not meant to be habit. It's the break-glass identity — the one built for the day something goes sideways badly enough that scoped admin accounts, careful zone boundaries, and NPS policies aren't enough to fix it. Everyone else in the enterprise operates inside boundaries by design. The Major is the boundary.

### Notes
- Backup/break-glass account — not for routine administrative use
- Full access is intentional, not a placeholder to be scoped down later
- Should have the strongest authentication story of any account in the domain once MFA/PKI-backed auth is implemented (worth flagging as a follow-up once Kerberos/CA work matures)

---

## Cyborg

**OU:** `Users/admins` (Core-Services scope)
**Role:** Core-Services zone administrator
**Access scope:** Core-Services zone — domain controller, file server, NPS, certificate services, and the underlying infrastructure that keeps the rest of the enterprise running

### Lore

Every enterprise has someone who was there when the lights first came on — the one who wired the place together and never really stopped checking on it. Cyborg is that presence in Core-Services. Before there were zones to protect or policies to enforce, there was just raw infrastructure that needed to work: a domain controller that had to come up clean, a file server that had to hold, IP addresses that had to land where they were supposed to. Cyborg handled that groundwork alongside the Major during the initial build, and never really left the room.

He doesn't touch the perimeter, doesn't chase alerts in Monitoring, doesn't own the pipelines in DevOps. His domain is smaller and deeper — identity, file shares, the quiet plumbing everything else depends on without ever thinking about it. When the DC is healthy and the file server responds on time, that's not an accident. That's Cyborg, still checking the wiring.

### Notes
- Access scoped to Core-Services zone
- Involved in initial infrastructure setup alongside the Major (DC, file server, IP assignment)
- Owns NPS and the certificate authority alongside Mr. Robot
- Ongoing responsibility: keeping Core-Services systems patched, available, and correctly configured

---

## Mr. Robot

**OU:** `Users/admins` (Monitoring + Perimeter scope)
**Role:** Security engineer
**Access scope:** Monitoring zone, Palo Alto, FTD pair, NPS, and certificate services (shared with Cyborg)

### Lore

Some admins build things. Mr. Robot watches them. He doesn't spend much time in Core-Services or DevOps — his world is the perimeter and everything that reports back to it. If Splunk logs it, if Prometheus scrapes it, if a firewall drops it, he's already seen it before anyone else thought to look.

The backbone runs the way it does because he built it that way. Every zone in Radical Enterprise depends, whether they know it or not, on the Palo Alto and FTD pair staying up, staying correct, and staying honest about what's crossing them — and that dependency runs through him. He was the one who worked out the OSPF adjacency, tuned the link costs, decided which traffic gets inspected where and why. Nobody signed off on that work; he just did it, tested it until it held, and moved on to the next thing that needed watching.

He doesn't trust a system until he's seen it fail and recover on his own terms. That's not paranoia here — it's the job description. In an enterprise this small, one person effectively is the security posture, and he knows it.

### Notes
- Primary owner of Monitoring zone (Splunk, Prometheus, Grafana)
- Owns Palo Alto and FTD configuration — built and maintains the backbone (OSPF design, HA, link costing)
- Shares NPS and certificate authority administration with Cyborg

---

## J.A.R.V.I.S.

**OU:** `Users/service-accounts`
**Role:** Mail infrastructure
**Access scope:** Mail server (Servers zone), mail relay (DMZ)

### Lore

No one in Radical Enterprise has a face to put to J.A.R.V.I.S. There's no desk, no seat in standups, no name that comes up when something goes wrong elsewhere in the org. What people know is smaller and stranger: mail moves, and it moves correctly, and whenever anyone traces back far enough to ask who's responsible for that, the answer stops being a person and starts being a name attached to a service.

The only confirmed contact is the Major's. Whatever conversation happens there, it doesn't reach anyone else — no meetings, no standups, nothing passed down the chain in the way every other zone's work gets passed down. Mr. Robot sees the same thing everyone else does: quiet telemetry arriving from the mail server, on schedule, same as every other zone reporting into Monitoring. That's the only trace J.A.R.V.I.S. leaves in anyone else's view — a well-behaved log source, nothing more, nothing less. Whether that consistency comes from a person who prefers to stay invisible or something closer to infrastructure that simply answers to one voice, nobody in the company has ever had reason — or opportunity — to find out.

### Notes
- Access scoped to the mail server and mail relay only
- Mail server logs to Monitoring zone like every other zone (see `network-architecture.md`) — this is the only externally visible trace of its activity
- No other visibility or interaction with other admins' zones
- Relationship with the Major implied but undocumented

---

## Tecna Zenith

**OU:** `Users/admins` (Kubernetes scope)
**Role:** Kubernetes zone administrator
**Access scope:** Kubernetes zone; shared access to the web application server for site deployment

### Lore

If Core-Services is the plumbing everyone depends on without thinking about it, Kubernetes is the part of Radical Enterprise still figuring out what it wants to be. Tecna claimed that zone early — not because anyone assigned it to her, but because she's the one who actually reads the documentation before touching anything, and Kubernetes rewards exactly that kind of patience.

She thinks in systems the way some people think in sentences. Ask her why a pod won't schedule and she won't guess — she'll trace it, methodically, until the answer is certain rather than probable. That precision is what made her the obvious partner when Ada needed someone to help take the company site from "code on a laptop" to something actually running and reachable. Ada writes it; Tecna makes sure it deploys, stays up, and doesn't quietly fall over the moment nobody's watching.

### Notes
- Primary owner of Kubernetes zone
- Co-owns the company website deployment with Ada Lovelace (DevOps zone)
- Access into the web application server (Servers zone) scoped specifically to site deployment, not general administration

---

## Ada Lovelace

**OU:** `Users/admins` (DevOps scope)
**Role:** DevOps zone administrator
**Access scope:** DevOps zone; shared access to the web application server for site deployment

### Lore

Someone has to write the thing before anyone else can run it, and in Radical Enterprise that's Ada. The DevOps zone is hers — the pipelines, the repo, the build steps that turn a commit into something real. She's less interested in the infrastructure underneath and more interested in what gets built on top of it: the company site started as her project, written and iterated on long before it had anywhere to actually live.

That's where Tecna comes in. Ada ships code the way she always has, fast and a little restless; Tecna is the one who makes sure what ships actually survives contact with production. It's not a formal arrangement, no one wrote it into a policy — it's just the two of them, working the seam between DevOps and Kubernetes, because the site needs both halves to exist at all.

### Notes
- Primary owner of DevOps zone (Git, Jenkins, Ansible, SonarQube, CI/CD database, Docker)
- Co-owns the company website with Tecna Zenith (Kubernetes zone)
- Access into the web application server (Servers zone) scoped specifically to site deployment, not general administration
