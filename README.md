# Home Lab 02: New-Device Watcher

After the network pass in [Home Lab 01](https://github.com/m4573rk4i/Home-lab-01-network-hardening), I wanted a repeatable check for MAC addresses the Mac mini can see on the main LAN that are missing from my approved list. A missing MAC can be a gadget I forgot, a guest on the main network, or a phone that rotated its Wi-Fi address. I wrote `watch.py` and scheduled it once a night.

Each run is a single snapshot. The script is idle between runs. The first MAC that showed up after the baseline was the Roomba, and I added it to the list on purpose.

## What a run does

`watch.py` sweeps one prefix, `192.168.1.0/24`. That is the stand-in I use for the home LAN, and it is the prefix hardcoded in the script. The sweep pings host numbers 1 through 254, 64 pings at a time. Each ping is one echo with a 300 millisecond wait (`ping -c 1 -W 300` on this Mac). A host that answers slower than that wait can be missed unless it was already cached.

After the pings finish, the script reads `arp -an` and keeps entries on that prefix whose line includes a MAC. The pattern matches the lowercase MAC text this Mac prints, then stores the MAC in uppercase. An incomplete ARP line has no MAC, so it is skipped. When the same MAC appears on more than one line, the later IP is the one kept.

The script compares those MACs with `known.json` in the script directory. On a normal run it appends one line to `watch.log`:

```text
<local time> seen=<count> new=<count> <address/MAC pairs for new MACs only>
```

The timestamp is local time with no timezone offset. This Mac is set to America/Phoenix. Pairs are written only for MACs missing from the list, which is why the log stays on the machine.

When `new` is greater than zero, the script asks macOS for a notification titled "New device on home network", with the sound Basso. The body is the count and the addresses, and the script prints `NEW:` plus the map. When nothing is new it prints `OK: <count> devices, none new`. A finished run exits 0 in both cases. I use the log line as the record.

## Reachability, and what an inventory would be

`seen` is the set of MACs in this Mac's ARP cache for that prefix after the ping sweep. A host that answered is likely to be there. A host that spoke on the LAN earlier can still be there after it goes quiet, because an ARP entry hangs around until it expires. A host that ignores ping and has no cache entry is absent from the count.

The membership records are the router client list, the access point association table, and the DHCP leases. This script never reads them. I keep those separate when I want a fuller inventory. The counts in this note are ARP snapshots, a different measurement from the router inventory in Home Lab 01.

Guest-network clients sit on their own network. The script keeps only the main LAN prefix, so a guest client is outside the result. The snapshot is also the wrong place to look for an authoritative member list of the main LAN.

## Schedule

`com.example.newdevice-watch.plist` is a user LaunchAgent template. `StartCalendarInterval` is hour 2, minute 0: 2:00 AM local time. The program is `/usr/bin/python3` running the script. Standard output goes to `launchd.out` and standard error goes to `launchd.err`. The paths in the file are `/path/to/newdevice-watch/...` placeholders. There is no `RunAtLoad` key, so logging in does not start a sweep.

I loaded the agent in my user session. The 2:00 run happens when I am logged in and the Mac is awake. November 8, described below, was that kind of night.

The other cases are launchd's documented `StartCalendarInterval` behavior, and I have not watched them on this Mac. Asleep at 2:00, with the same session still logged in: the missed job runs once on wake, and several missed nights fold into that one run. Powered off through 2:00: the job waits for the next 2:00 the machine is on. Logged out, or sitting at the login window: this user agent is unloaded, so 2:00 can pass with no run.

## Usage

```text
python3 watch.py --baseline
python3 watch.py
```

`known.example.json` shows the shape: one placeholder MAC (`AA:BB:CC:DD:EE:FF`), a name, and a placeholder address. The real list stays on the Mac.

`--baseline` records every MAC observed on that run. The same thing happens when `known.json` is missing or empty, even without the flag. Each new MAC is stored with a blank name and the address from the snapshot. MACs already in the file keep their saved name and first address. MACs that were absent this time stay in the file. The baseline path prints `Baseline saved: <count> devices` and returns. It does not append to `watch.log`, and it does not notify.

The flag approves the whole snapshot. I use it only after I have reviewed every observed address and I mean to approve all of them. To approve one device, I add that single MAC to `known.json`. Using `--baseline` to clear one alert would also approve every other address in the cache, including a stale entry or someone who happened to be on the main LAN during the sweep.

## Runs I checked

The first baseline saved 28 devices: the MACs visible to that sweep.

The next run reported one unknown MAC. I checked it and it was the Roomba. It was asleep or otherwise absent for the baseline, then present for the later snapshot. I added it to the approved list on purpose. The hours between those two runs were invisible to the script.

The approved list has 29 entries after that addition.

On November 8, 2026, at 2:00:11 AM Phoenix time, the scheduled run logged `seen=29 new=0`. I counted 29 entries in the approved list. The LaunchAgent had 1 run and a last exit status of 0, and the error log was empty. That run had nothing new, so it never called `osascript`. I have not made a separate test that Notification Center shows the banner.

## Limits I keep in mind

- The sweep is the main LAN prefix. Guest clients are outside it. The result is the ARP cache snapshot.
- A stale ARP entry can keep a device in `seen` after it has left.
- A device can be asleep, silent to ping, slower than the 300 ms wait, or present only between runs. I can miss devices, and I can miss joins.
- A phone using a private Wi-Fi address can rotate its MAC and look new.
- A spoofed MAC that matches an approved entry is treated as that device. The script has no second check on who is using the address.
- Notification delivery is still unchecked. The November 8 run did not exercise that path.

## Local files

`.gitignore` names `known.json`, `watch.log`, `launchd.out`, and `launchd.err`. Git will leave those untracked files out of a later commit. An ignore rule leaves an already tracked file tracked. I checked this repo's history: those four names are not in any commit. The tracked example uses the placeholder MAC and address only.

## What's next

- Look up the vendor from the MAC prefix when a run reports an unknown.
- Send the alert to my phone. The only alert in the script today is the local notification, and I still need to confirm it appears.
- Graph the seen and new counts next to my AdGuard Home DNS stats.

## Study note

Topics I am practicing here: asset inventory, monitoring, and scripting. Those are the same Security+ SY0-701 study topics I mapped in Home Lab 01.
