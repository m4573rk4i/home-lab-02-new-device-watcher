# Home Lab 02: New-Device Watcher

After hardening my home network in [Home Lab 01](https://github.com/m4573rk4i/Home-lab-01-network-hardening), I wanted to know when something new joins it. A device I don't recognize could be a guest, a new gadget, or something that shouldn't be there. So I wrote a small Python script that runs every night on my Mac mini and tells me.

## How it works

1. Pings every address in my home subnet (192.168.1.1–254) in parallel to wake up the ARP table.
2. Reads the ARP table (`arp -an`) to get the MAC address and IP of everything that answered.
3. Compares each MAC against `known.json`, my list of approved devices.
4. If anything is unknown, it posts a macOS notification with the IP and logs it. Every run is logged either way.

It runs at 2 AM through a macOS LaunchAgent (`launchd`), the Mac's built-in scheduler.

## Usage

```
python3 watch.py --baseline   # record everything online now as known
python3 watch.py              # check for new devices
```

To approve a device after an alert, re-run with `--baseline` or add its MAC to `known.json`. `known.example.json` shows the format; my real list stays out of the repo.

## First run

The baseline caught 28 devices. On the very next run the watcher flagged one new device, which turned out to be our Roomba waking from sleep after the baseline was taken. Good proof that it works, and a reminder that a baseline only captures what's awake.

## Limits I know about

- It only sees the main network, not the isolated guest/IoT network.
- Devices asleep at 2 AM are missed until they're online during a run.
- Phones using private Wi-Fi addresses can rotate their MAC and trigger a false alarm.
- ARP can be spoofed, so this is awareness, not a security control.

## What's next

- Look up the device maker from the MAC prefix in the alert.
- Send alerts to my phone instead of only the Mac.
- Feed results into a Grafana dashboard alongside my AdGuard Home DNS stats.

## Security+ topics this touches

Asset inventory and management, network reconnaissance, monitoring and alerting, and scripting/automation.
