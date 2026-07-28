# 01 - FTD Initial Config

These are the steps for the initial configuration of the FTD. In many ways, this mirrors what was done in the Palo Alto lab, but from the Cisco perspective.

## CLI Bootstrap

This initial CLI configuration applies to the **management interface** — the outside data interface (g0/0) is configured separately later, through the GUI wizard.

```
> configure network hostname FTD
Hostname update is partially complete. Deploy changes from Secure Firewall Device Manager to complete the update so that the same name is used by all system processes.

> configure network ipv4 manual 192.168.10.18 255.255.255.240 192.168.10.17

Setting IPv4 network configuration...
Network settings changed.

> configure network dns 10.10.10.10 208.67.222.222
```

I set my domain controller (handling internal DNS) as the primary DNS server, so I can use FQDNs on internal rules. OpenDNS is set as a backup, so I can still resolve externally if my DC is ever fully down.

Once this is done, you can log in using `https://<yourIP>`.

![alt text](01-initial-gui.png)

## GUI Setup Wizard

You can go through the guided configuration or skip it. I went through it, since my topology purposely matches g0/0 to be the interface assigned to the **outside** security zone.

![alt text](02-set-outsideint.png)

Here I set my outside IP, which is the transit network pointing to my Palo Alto firewall on the perimeter. IPv6 was disabled.

Then I set NTP. My DC's PDC emulator is the time authority, so I pointed it to my DC IP. No NTP authentication was configured for this lab.

![alt text](03-ntp-settings.png)

### Registration

Next it asks you to register. Since I'm running this in CML, I used the 90-day eval license. I keep backups up to date so I can replace my firewall when the license ends — I just wipe the device and upload the backup to the new one. I selected **FTDv10 - 1 Gbps**, which requires a minimum of 4 cores and 8 GB RAM. Keep in mind that with those specs, the license could actually go up to FTDv20 - 3 Gbps, but nothing further than that.

![alt text](04-register-evallicense.png)

Then you select the device mode. I chose standalone so it can be managed from the GUI.

![alt text](05-standalone.png)

## Post-Setup Cleanup

### Delete the auto-configured NAT

One of the first things I do is delete the NAT rule that gets auto-configured during initial setup, since it isn't needed for this topology.

Go to **Policies > NAT** and use the trash icon on the right of the rule.

![alt text](06-delete-nat.png)

### Delete the default security policy

You can also delete the default security policy — an inside-to-outside "allow" rule. The default NAT and this default policy exist mainly so the FTD can get updates and reach Cisco for license info.

Notice the default action is **block** (marked in green in the screenshot).

![alt text](07-default-securitypolicy.png)

### Delete the default static route

Go to **Device**, then check **Routing** — there's a static route already set.

![alt text](08-device-routing.png)

This is a match-all route acting as a default route. We can delete it — in this lab topology, the default route is learned from the Palo Alto via OSPF instead.

![alt text](09-default-route.png)

> **Note:** As with any FTD change, remember to deploy whenever you want your pending changes to take effect and become part of the running configuration.

## Syslog / Log Forwarding

Go to **Device > Logging Settings**.

![alt text](12-loggingsettings.png)

Activate **Data Logging**, then click the plus sign to add a syslog server. Since I had no previous object, I used **Create New**.

I added my Splunk server IP on port 514/UDP. Unlike Palo Alto, FTD only supports UDP on 514 — if you want TCP, port 1470 is the one recommended directly by the FTD itself. I actually wanted to run 514/TCP, since I've set it up that way on other devices before, but FTD won't allow it. If you try, you'll get: *"Invalid port for Syslog Server. Either use the default ports, which are 514 for UDP or 1470 for TCP, or specify a port in the 1025-65535 range."* Lastly, select the interface that can reach your server.

![alt text](13-addsyslogserv.png)

For severity filtering I chose **Informational**, since I want more logs to analyze on Splunk for a future lab.

![alt text](14-severityfiltering.png)

Save the changes.

## Deploying Changes

Go to **Deploy**.

![alt text](17-deploy.png)

On the left side, under actions, there are a few options including **Discard** if you want to discard the pending changes.

![alt text](15-discarddeploy.png)

On the right side you can just deploy, or name the deployment first — useful as a description so it's easier to find later.

![alt text](16-name-or-deploy.png)

At this point the device will send firewall logs to the syslog server. If you also want access control rule logs, you have to enable logging on the rule directly — this lab doesn't go deeper into that, since there will be a dedicated lab for security policies.

There is no banner setting on FTD — instead you can edit the login page.

![alt text](image-50.png)

## Backup & Restore

Go to **Device > Backup and Restore**.

![alt text](19-bckupandrestore.png)

My Smart License expires in 18 days, so I set a scheduled backup 3 days before that, in case I forget to take a fresh backup before deleting the firewall (I wipe it once the license is over, to redeploy with a new eval license).

I chose the scheduled backup option.

![alt text](20-schedule-backup.png)

You can name the backup, set a description, and the date/time. Be careful setting (and remembering) the password — you'll need it to actually use the backup. Losing it is effectively the same as having no backup at all; this has happened to me before.

![alt text](21-backup1.png)

Feel free to also explore the manual backup option.
