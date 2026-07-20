# Access Layer Switch Hardening Lab

A hands-on walkthrough for securing a Cisco IOS access-layer switch: management access, trunk/access port config, port security, spanning-tree protections, and DHCP snooping. Written from a real lab build — every command here was run and verified, including a couple of the "wait, why did that happen" moments left in on purpose.

## Who this is for

Anyone comfortable with basic Cisco IOS CLI navigation who wants a practical, opinionated pass at access-layer hardening — not just a command dump, but the reasoning behind each choice.

> Derived from the main lab configuration in REL.

## Lab topology

You only need **Cisco Modeling Labs (CML) — Free/Personal tier** to complete this lab. No physical hardware required, and a single IOSv/IOSvL2 switch node is all you need — the trunk, access, and security config here can all be built and verified on that one node.

**Minimum hardware to run CML (per Cisco's official system requirements):**

| Resource | Minimum |
|---|---|
| Memory | 8 GB (allocated to the CML VM) |
| CPU | 4+ physical cores, Intel processor supporting VT-x and EPT |
| Network | 1 interface |
| Disk | 32 GB or more |

- No DHCP server on these VLANs (this matters later — see the DAI note)

Swap VLAN numbers, interface names, and IPs for your own topology as you go.

---

## Step 1 — Basic identity and local management access

Enter privileged EXEC, then global config:

```
inserthostname-here>enable
inserthostname-here#configure terminal
```

Set the hostname, enable secret, and password encryption service. The encryption service isn't strong crypto, but it stops plaintext passwords from being visible in a casual `show run`:

```
inserthostname-here(config)#hostname access-sw
access-sw(config)#enable secret <your-secret>
access-sw(config)#service password-encryption
```

Create a local user for SSH login (used instead of relying only on the enable secret):

```
access-sw(config)#username <your-username> privilege 15 secret <your-secret>
```

## Step 2 — SSH access (not Telnet)

SSH needs a domain name and an RSA keypair before it will work. If you try to generate the key first, IOS will stop you:

```
inserthostname-here(config)#crypto key generate rsa
% Please define a domain-name first.
```

So set the domain name first, *then* generate the key:

```
access-sw(config)#ip domain name radicaldc.lab
access-sw(config)#crypto key generate rsa
```

You'll be prompted for a modulus size — 2048 is a reasonable minimum:

```
How many bits in the modulus [2048]: 2048
% Generating 2048 bit RSA keys, keys will be non-exportable...
```

Force SSHv2 (v1 has known weaknesses) and lock the VTY lines down to SSH only, using the local user database for auth:

```
access-sw(config)#ip ssh version 2
access-sw(config)#line vty 0 4
access-sw(config-line)#login local
access-sw(config-line)#transport input ssh
access-sw(config-line)#exec-timeout 5 0
```

**Check how many VTY lines your platform actually has** before assuming `0 4`:

```
access-sw(config)#line vty 0 ?
  <1-4>  Last Line number
```

## Step 3 — NTP and login protections

Accurate timestamps matter for correlating security events later (port-security violations, BPDU guard trips, failed logins), so set NTP:

```
access-sw(config)#ntp server 198.18.128.1
```

Protect the console line with an idle timeout so a forgotten session doesn't sit open indefinitely:

```
access-sw(config)#line console 0
access-sw(config-line)#exec-timeout 10 0
```

Log failed login attempts and rate-limit them to blunt brute-force attempts against SSH/console:

```
access-sw(config)#login on-failure log
access-sw(config)#login block-for 120 attempts 5 within 60
```

This blocks further login attempts for 120 seconds if there are 5 failures within a 60-second window.

---

## Step 4 — Trunk interfaces

Uplinks toward the firewall/router get a description (always label your ports — future you will thank you), 802.1q encapsulation, an explicit allowed-VLAN list, and trunk mode:

```
access-sw(config)#interface ethernet0/0
access-sw(config-if)#description trunk-port-2d-internal-ftd
access-sw(config-if)#switchport trunk encapsulation dot1q
access-sw(config-if)#switchport trunk allowed vlan 10,20,30,40,50
access-sw(config-if)#switchport mode trunk
```

Repeat for any additional trunk uplinks.

## Step 5 — Access ports and VLANs

**The quick way** — assign a VLAN directly on an interface before it exists, and IOS creates it for you automatically:

```
access-sw(config-if)#interface e0/2
access-sw(config-if)#switchport access vlan 10
% Access VLAN does not exist. Creating vlan 10
```

This works, but leaves the VLAN unnamed and the port's negotiation settings on defaults. Checking the interface confirms it:

```
access-sw#show interfaces e0/2 switchport | i Administrative Mode|Negotiation
Administrative Mode: dynamic auto
Negotiation of Trunking: On
```

`dynamic auto` + trunk negotiation **on** means this port will still negotiate DTP with whatever's plugged into it — not ideal for an access port that should never become a trunk.

**The preferred way** — create and name the VLAN first, then explicitly set the port to access mode:

```
access-sw(config)#vlan 20
access-sw(config-vlan)#name devops-zone
access-sw(config-vlan)#interface e0/3
access-sw(config-if)#switchport mode access
access-sw(config-if)#switchport access vlan 20
access-sw(config-if)#end
```

Verify the difference:

```
access-sw#show interfaces e0/3 switchport | i Administrative Mode|Negotiation
Administrative Mode: static access
Negotiation of Trunking: Off
```

`static access` with negotiation **off** — this port is locked into access mode and won't negotiate trunking under any circumstance. This is the state every access port should end up in.

---

## Step 6 — Port security

Enable port security, set the violation action, and cap the MAC count per port:

```
access-sw(config)#interface e0/2
access-sw(config-if)#switchport port-security
access-sw(config-if)#switchport port-security violation restrict
access-sw(config-if)#switchport port-security maximum 5
```

**Violation modes, briefly:**
- `shutdown` — err-disables the whole port on a violation. Risky on a link carrying multiple hosts, since one bad MAC takes everyone down.
- `restrict` — drops only the offending traffic and logs it, leaving everything else on the port working. Better default for shared/multi-host access ports.
- `protect` — drops silently, no log. Rarely what you want.

**Static vs. sticky MAC entries** — pick based on what the port needs:

- **Static**, when you need to *exclude* specific known devices from a segment (e.g., a management backdoor you don't want counted as a valid host):
  ```
  access-sw(config-if)#switchport port-security mac-address <server-mac>
  ```
  Repeat per MAC. Because `maximum` caps the total, explicitly listing only the MACs you want leaves no room for anything else to sneak in — even without ever typing a "block" rule.

- **Sticky**, for ports where you're fine auto-learning whatever's currently connected and want it saved into the running config as if typed manually:
  ```
  access-sw(config-if)#switchport port-security mac-address sticky
  ```
  Caveat: sticky learns whatever is *actively transmitting* at the moment you enable it. If you have any device on that segment you don't want locked in (like a backdoor interface), it can get learned right along with everything else — sticky isn't a good fit for that scenario.

> **Note on `maximum`:** don't just count physical devices — count MACs. A single server can present more than one MAC to the same link via NIC teaming/bonding, multiple physical NICs landing on the same switch port, hypervisor VMs bridged out an interface, or shared-mode iLO/iDRAC/IPMI. Check `show mac address-table interface <port>` against what you expect *before* locking the number in. Also consider leaving headroom (or skipping `maximum` for a fixed low default) on ports where the device mix is still evolving — e.g., a Kubernetes node where CNI networking can shift MAC behavior over time.

## Step 7 — DTP, native VLAN, and spanning-tree protections (access ports)

Applied as a range across all access ports:

```
access-sw(config)#interface range e0/2-3,e1/0-2
access-sw(config-if-range)#switchport nonegotiate
access-sw(config-if-range)#switchport trunk native vlan 99
access-sw(config-if-range)#spanning-tree portfast
access-sw(config-if-range)#spanning-tree bpduguard enable
```

- `nonegotiate` — access ports don't need DTP negotiation; disabling it removes a needless negotiation surface.
- Native VLAN moved off the default (VLAN 1) to a dedicated, unused VLAN — reduces exposure to VLAN-hopping techniques that rely on the default native VLAN.
- `portfast` — access ports go straight to forwarding instead of cycling through STP listening/learning states, since no switch should ever be downstream of them.
- `bpduguard enable` — if a switch (or looping device) ever *does* get plugged into one of these ports and starts sending BPDUs, the port is immediately err-disabled rather than being allowed to participate in the spanning tree.

## Step 8 — Disable unneeded services, set the banner

Turn off the HTTP/HTTPS management server — SSH is the intended management path, no reason to leave a web GUI listening:

```
access-sw(config)#no ip http server
access-sw(config)#no ip http secure-server
```

Set a login banner. Keep it professional even in a lab — it's a habit worth having, and in production this text can matter legally for pursuing unauthorized access:

```
access-sw(config)#banner motd ^
AUTHORIZED ACCESS ONLY - IF YOU ARE IN THIS MESSAGE WINDOW AND ARE NOT AUTHORIZED CONTACT <your-contact>
^
```

(Use any delimiter character that won't appear in your message body — `^`, `#`, `~` all work.)

## Step 9 — Unused ports

Every physical port not actively in use gets parked in an unused/blackhole VLAN and administratively shut down — closes off the easiest possible entry point (someone walking up and plugging into an empty port):

```
access-sw(config)#interface range e1/3,e2/0-3
access-sw(config-if-range)#switchport mode access
access-sw(config-if-range)#switchport access vlan 999
access-sw(config-if-range)#description unused-ports
access-sw(config-if-range)#shutdown
access-sw(config-if-range)#exit
```

## Step 10 — DHCP snooping

Enable globally and per-VLAN:

```
access-sw(config)#ip dhcp snooping
access-sw(config)#ip dhcp snooping vlan 10,20,30,40,50
```

Worth enabling even with **no DHCP server present**. Every port defaults to untrusted, so any rogue DHCP server plugged in later gets its offers/acks dropped automatically. It also lays the groundwork for Dynamic ARP Inspection and IP Source Guard, both of which depend on the DHCP snooping binding table.

### A note on Dynamic ARP Inspection (intentionally skipped here)

DAI wasn't enabled in this lab. Reasoning: DAI validates ARP traffic against the DHCP snooping binding table — but with no DHCP server, that table stays empty, so DAI has nothing to validate against unless you also build static ARP ACLs mapping every host's IP to its MAC by hand:

```
! Example only — not applied in this lab
arp access-list STATIC-HOSTS
 permit ip host <server1-ip> mac host <server1-mac>
 permit ip host <server2-ip> mac host <server2-mac>

ip arp inspection filter STATIC-HOSTS vlan 10
ip arp inspection vlan 10
```

For a small, known lab topology, the manual-mapping overhead outweighs the benefit (protection against ARP spoofing/poisoning within the segment). Worth revisiting if a real DHCP server gets added later, since bindings would then populate automatically and DAI could run without static ACLs.

## Step 11 — Errdisable auto-recovery

BPDU guard (and other errdisable causes) will take a port down and leave it down until manually recovered — annoying in a lab where cables get moved around often. Auto-recovery brings it back up after a timer instead of requiring a manual `shutdown` / `no shutdown`:

```
access-sw(config)#errdisable recovery cause bpduguard
access-sw(config)#errdisable recovery interval 300
```

300 seconds (5 minutes) is a reasonable default — long enough not to mask a genuinely flapping problem, short enough not to leave a port down indefinitely by accident.

Verify:

```
access-sw#show errdisable recovery
```

---

## Verification checklist

Run these after each stage to confirm things landed the way you expect:

```
show run interface <if>                              " confirm interface-level config
show interfaces <if> switchport | i Administrative Mode|Negotiation
show port-security interface <if>                     " current MAC count, violation mode
show mac address-table interface <if>                  " what's actually learned
show ip dhcp snooping                                  " snooping status per VLAN
show ip dhcp snooping binding                           " binding table (empty if no DHCP server)
show errdisable recovery                                " confirm auto-recovery causes/timer
show spanning-tree interface <if> detail                " confirm portfast + bpduguard state
```

---

## Full reference configuration

The complete raw switch config (all interfaces, full running-config) is kept separately in this lab's GitHub repo rather than duplicated here: [Access Switch](../configs/access-switch.conf)

Use the steps above to understand the *why* behind each block; use the linked config as the source of truth for the *exact* end state.

---

## Summary of decisions and why

| Choice | Reasoning |
|---|---|
| `restrict` over `shutdown` for port security | Shared access ports carry multiple hosts; one bad MAC shouldn't kill the whole link |
| Static MACs on the core port | Needed to explicitly exclude a known backdoor management interface from the allowed set |
| Sticky MACs elsewhere | Faster to deploy, fine where there's nothing on the segment that needs excluding |
| No fixed `maximum` on the k8s port | MAC behavior there is still evolving (CNI networking); a hard cap would fight normal operation |
| Native VLAN moved to 99 | Reduces exposure to VLAN-hopping techniques targeting the default native VLAN |
| DHCP snooping on with no DHCP server | Still blocks rogue DHCP servers on untrusted ports; lays groundwork for DAI/IPSG later |
| DAI skipped | No DHCP server means an empty binding table; static ARP ACLs are the only alternative, and the manual overhead isn't worth it for this topology size |
| Errdisable auto-recovery for BPDU guard | Avoids manual intervention every time a cable move trips the guard |
