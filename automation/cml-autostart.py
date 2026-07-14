# CML Startup Automation

## Purpose

A small Python script that automatically starts the REL lab in CML. This isn't just a reboot-recovery convenience — because the lab runs on dCloud, the entire environment has to be started fresh on every new session spin-up, not just after a host restart. Without this, starting REL would mean manually going into the CML UI every single time a new dCloud session begins.

## Script

```python
from virl2_client import ClientLibrary
import time
import os

# Wait a bit on boot for the environment to be ready
time.sleep(240)

client = ClientLibrary(
        os.getenv("CML_HOST"),
        os.getenv("CML_USER"),
        os.getenv("CML_PASS"),
        allow_http=False,
        ssl_verify=False  # It will change once a certificate is assigned
)

# Find and start lab by name
labs = client.find_labs_by_title("REL")
if labs:
    lab = labs[0]
    print(f"Starting LAB: {lab.title}")
    lab.start()
else:
    print("Lab 'REL' not found!")
```

## How it works

1. **Boot delay** — sleeps for 240 seconds before doing anything. This isn't just general startup timing; it works around a specific dCloud behavior where the CML API can report the environment as ready before the underlying VM image delta has actually finished attaching. Without this delay, nodes have failed to start in the past — the API looked healthy, but the actual VM image data wasn't there yet. This is especially significant for custom node images that aren't part of the default dCloud CML VM — such as the Palo Alto image used in this lab — since those images specifically depend on the delta finishing before they can start, making them more exposed to this timing issue than default/stock images would be.
2. **Authentication** — connects to the CML controller via `ClientLibrary`, using credentials pulled from environment variables (`CML_HOST`, `CML_USER`, `CML_PASS`) rather than hardcoded values.
3. **TLS** — `ssl_verify=False` is used because CML's cert is self-signed in this lab; acceptable here since it's a closed lab environment talking to a known host, but wouldn't be appropriate against a cert you don't control.
4. **Lab lookup and start** — searches for a lab titled `"REL"` and starts it if found; logs a clear message either way (started, or not found).
