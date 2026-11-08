#!/usr/bin/env python3
"""New-device watcher: sweeps the LAN, compares MACs to known.json, alerts on unknowns."""
import json, re, subprocess, sys, datetime, pathlib, concurrent.futures as cf
HERE = pathlib.Path(__file__).resolve().parent
KNOWN, LOG = HERE / "known.json", HERE / "watch.log"
SUBNET = "192.168.1"

def sweep():
    def ping(i): subprocess.run(["ping","-c1","-W300",f"{SUBNET}.{i}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    with cf.ThreadPoolExecutor(64) as ex: list(ex.map(ping, range(1,255)))
    out = subprocess.run(["arp","-an"],capture_output=True,text=True).stdout
    seen = {}
    for ip, mac in re.findall(r"\((\d+\.\d+\.\d+\.\d+)\) at ([0-9a-f:]+)", out):
        if not ip.startswith(SUBNET + "."): continue
        mac = ":".join(p.zfill(2) for p in mac.split(":")).upper()
        seen[mac] = ip
    return seen

def notify(msg):
    subprocess.run(["osascript","-e",f'display notification "{msg}" with title "New device on home network" sound name "Basso"'])

def main():
    seen = sweep()
    known = json.loads(KNOWN.read_text()) if KNOWN.exists() else {}
    if "--baseline" in sys.argv or not known:
        for mac, ip in seen.items(): known.setdefault(mac, {"name": "", "first_ip": ip})
        KNOWN.write_text(json.dumps(known, indent=2)); print(f"Baseline saved: {len(known)} devices"); return
    new = {m: ip for m, ip in seen.items() if m not in known}
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    with LOG.open("a") as f:
        f.write(f"{stamp} seen={len(seen)} new={len(new)} {' '.join(f'{ip}/{m}' for m, ip in new.items())}\n")
    if new:
        notify(f"{len(new)} unknown: " + ", ".join(new.values()))
        print("NEW:", new)
    else:
        print(f"OK: {len(seen)} devices, none new")

if __name__ == "__main__": main()
