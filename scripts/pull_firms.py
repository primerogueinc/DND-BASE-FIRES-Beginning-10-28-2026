#!/usr/bin/env python3
"""Pull NASA FIRMS near-real-time detections for a box around a DND base and build a merged table.

Usage:
    FIRMS_MAP_KEY=<your key> python3 scripts/pull_firms.py <out_dir> <west,south,east,north> <days 1-5> <ref_lat> <ref_lon> <utc_offset_hours>

Example (CFB Gagetown, ADT = UTC-3):
    python3 scripts/pull_firms.py cfb-gagetown/2026-10-29/firms -66.6,45.55,-65.9,46.0 2 45.749 -66.260 -3

The map key is read from the environment and is never written to disk.
Raw API responses are saved unaltered in <out_dir>/raw/; the merged table adds UTC and local times
and the distance of each detection from the reference point.
"""
import csv, io, os, sys, urllib.request, hashlib, datetime as dt
from math import radians, sin, cos, asin, sqrt

SOURCES = ["VIIRS_NOAA21_NRT", "VIIRS_NOAA20_NRT", "VIIRS_SNPP_NRT", "MODIS_NRT", "LANDSAT_NRT"]


def km(a, b, c, d):
    a, b, c, d = map(radians, (a, b, c, d))
    return 2 * 6371 * asin(sqrt(sin((c - a) / 2) ** 2 + cos(a) * cos(c) * sin((d - b) / 2) ** 2))


def main():
    out, bbox, days, rlat, rlon, off = sys.argv[1:7]
    rlat, rlon, off = float(rlat), float(rlon), float(off)
    key = os.environ["FIRMS_MAP_KEY"]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%MZ")
    os.makedirs(f"{out}/raw", exist_ok=True)
    rows = []
    for s in SOURCES:
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{s}/{bbox}/{days}"
        body = urllib.request.urlopen(url, timeout=90).read()
        path = f"{out}/raw/{s}_{stamp}_{days}d.csv"
        open(path, "wb").write(body)
        print(path, hashlib.sha256(body).hexdigest())
        for r in csv.DictReader(io.StringIO(body.decode())):
            t = dt.datetime.strptime(r["acq_date"] + r["acq_time"].zfill(4), "%Y-%m-%d%H%M")
            r["source"] = s
            r["utc"] = t.strftime("%Y-%m-%d %H:%M")
            r["local"] = (t + dt.timedelta(hours=off)).strftime("%Y-%m-%d %H:%M")
            r["km_from_ref"] = round(km(rlat, rlon, float(r["latitude"]), float(r["longitude"])), 2)
            rows.append(r)
    rows.sort(key=lambda r: r["utc"])
    cols = ["utc", "local", "source", "satellite", "latitude", "longitude", "frp", "confidence",
            "daynight", "scan", "track", "km_from_ref"]
    with open(f"{out}/detections_{stamp}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "detections")


if __name__ == "__main__":
    main()
