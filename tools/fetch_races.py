#!/usr/bin/env python3
"""fetch_races.py: San Diego races for /san-diego-races/ (Tyler 2026-11-19: "an easy well designed way to see
what 5ks, 10ks, half marathons, and marathons are in the san diego area").

Sources, merged into data/races.json:
  1. RunSignup's races API (/Rest/races, running races within RADIUS miles of ZIP, today to +12 months).
     Their API Developer Contract says to register before use; the key lives outside git in
     ~/.brain-staging/runsignup/creds.json {"api_key": "...", "api_secret": "...", "affiliate_token": "..."}.
     No key file -> no fetch; the page keeps the last data. Calls run one at a time (their limit is 2 at once).
  2. data/majors.json: big races not on RunSignup (Carlsbad, Rock 'n' Roll, AFC, San Diego Half), dates read
     from each race's own page and dated in the file. Checked by hand when a date passes.

    python3 tools/fetch_races.py                 # fetch RunSignup + merge majors -> data/races.json
    python3 tools/fetch_races.py --from FILE     # build from a saved RunSignup response (one JSON page per line)

Only the four distances count (5K, 10K, half, marathon); kids' runs, 1-milers, virtual and private events are left
out; other distances on the same day (10 miles, 12K) are kept as a note. Past races drop off on every build.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "races.json"
MAJORS = ROOT / "data" / "majors.json"
CREDS = Path.home() / ".brain-staging" / "runsignup" / "creds.json"
ZIP, RADIUS = "92124", 35
KM = {"5K": 5.0, "10K": 10.0, "Half": 21.0975, "Marathon": 42.195}
ORDER = ["5K", "10K", "Half", "Marathon"]
SKIP_EVENT = re.compile(r"virtual|kid|youth|tot|toddler|diaper|fun run|1k\b|1 ?mile|mile fun|walk only|volunteer|untimed", re.I)


def to_km(dist):
    m = re.match(r"\s*([\d.]+)\s*(k|km|mi|mile|miles|m|meters)?\b", (dist or "").lower())
    if not m:
        return None
    n, u = float(m.group(1)), (m.group(2) or "")
    if u in ("k", "km"):
        return n
    if u in ("mi", "mile", "miles"):
        return n * 1.609344
    if u in ("m", "meters"):
        return n / 1000
    return None


def bucket(dist, name):
    """'5K' / '10K' / 'Half' / 'Marathon', or None. Distance first; the event name when the distance is missing or wrong."""
    km = to_km(dist)
    if km:
        for b, k in KM.items():
            if abs(km - k) / k < 0.03:
                return b
    n = (name or "").lower()
    if re.search(r"half|13\.1", n):
        return "Half"
    if re.search(r"marathon|26\.2", n):
        return "Marathon"
    if re.search(r"\b10\s?k\b|6\.2", n):
        return "10K"
    if re.search(r"\b5\s?k\b|3\.1", n):
        return "5K"
    return None


def other_label(dist):
    km = to_km(dist)
    if not km or km < 2:
        return None
    m = re.match(r"\s*([\d.]+)\s*(k|km|mi|mile|miles)", dist.lower())
    if not m:
        return None
    n = m.group(1).rstrip("0").rstrip(".") if "." in m.group(1) else m.group(1)
    return f"{n} mi" if m.group(2).startswith("mi") else f"{n}K"


KEEP_CAPS = {"XTERRA", "USA", "AFC", "CVC", "YMCA", "MLK", "PB&J", "SD"}


def clean_name(name):
    name = re.sub(r"^\s*(20\d\d)\s+", "", name or "")
    name = " ".join(w.capitalize() if w.isalpha() and w.isupper() and len(w) >= 3 and w not in KEEP_CAPS else w for w in name.split())
    name = re.sub(r"\s+(20\d\d)\s*$", "", name)
    name = re.sub(r"^PRE-SALE\s+", "", name, flags=re.I)
    return re.sub(r"\s+", " ", name).strip()


def mdy(s):
    return dt.datetime.strptime(s.split()[0], "%m/%d/%Y").date()


def from_runsignup(race, token=""):
    if not race.get("next_date"):
        return None
    if race.get("is_private_race") == "T" or race.get("is_draft_race") == "T":
        return None
    if re.search(r"virtual|test race", race.get("name", ""), re.I):
        return None
    dists, other, start = set(), set(), None
    for e in race.get("events") or []:
        if SKIP_EVENT.search(e.get("name") or ""):
            continue
        b = bucket(e.get("distance"), e.get("name"))
        if b:
            dists.add(b)
            t = (e.get("start_time") or "").split()
            if len(t) == 2 and (start is None or t[1] < start):
                start = t[1]
        elif (lab := other_label(e.get("distance"))):
            other.add(lab)
    if not dists:
        return None
    url = race.get("url") or ""
    if token and url:
        url += ("&" if "?" in url else "?") + "aflt_token=" + urllib.parse.quote(token)
    a = race.get("address") or {}
    return {"id": f"rsu-{race['race_id']}", "name": clean_name(race["name"]), "date": mdy(race["next_date"]).isoformat(),
            "end": mdy(race.get("next_end_date") or race["next_date"]).isoformat(),
            "city": (a.get("city") or "").strip().title().replace("Sandiego", "San Diego"),
            "distances": [d for d in ORDER if d in dists], "other": sorted(other), "start": start,
            "url": url, "source": "RunSignup"}


def fetch_runsignup(creds, start, end):
    races, page = [], 1
    while True:
        q = {"format": "json", "events": "T", "event_type": "running_race", "zipcode": ZIP, "radius": RADIUS,
             "start_date": start.isoformat(), "end_date": end.isoformat(), "results_per_page": 100, "page": page,
             "api_key": creds["api_key"], "api_secret": creds["api_secret"]}
        req = urllib.request.Request("https://runsignup.com/Rest/races?" + urllib.parse.urlencode(q),
                                     headers={"User-Agent": "tothefinish.ai race list (weekly)"})
        with urllib.request.urlopen(req, timeout=60) as r:
            got = json.load(r).get("races", [])
        races += got
        if len(got) < 100:
            return races
        page += 1
        time.sleep(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", help="saved RunSignup response, one JSON page per line")
    a = ap.parse_args()
    today = dt.date.today()
    if a.src:
        raw = []
        for line in Path(a.src).read_text().splitlines():
            if line.strip():
                raw += json.loads(line).get("races", [])
        token = ""
    else:
        if not CREDS.exists():
            sys.exit(f"no RunSignup key at {CREDS}: register at runsignup.com/API first; keeping the last data")
        creds = json.loads(CREDS.read_text())
        raw = fetch_runsignup(creds, today, today + dt.timedelta(days=365))
        token = creds.get("affiliate_token", "")
    rows, seen = [], set()
    for x in raw:
        r = from_runsignup(x.get("race", x), token)
        if not r or r["date"] < today.isoformat():
            continue
        key = (re.sub(r"[^a-z0-9]", "", r["name"].lower()), r["date"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(r)
    majors = json.loads(MAJORS.read_text())["races"] if MAJORS.exists() else []
    names = {re.sub(r"[^a-z0-9]", "", r["name"].lower()) for r in rows}
    for m in majors:
        if m["date"] >= today.isoformat() and re.sub(r"[^a-z0-9]", "", m["name"].lower()) not in names:
            rows.append({**m, "source": "race site"})
    rows.sort(key=lambda r: (r["date"], r["name"]))
    OUT.write_text(json.dumps({"updated": today.isoformat(), "near": f"{RADIUS} miles of San Diego",
                               "races": rows}, indent=1) + "\n")
    print(f"races: {len(rows)} ({sum(r['source'] == 'RunSignup' for r in rows)} RunSignup, "
          f"{sum(r['source'] != 'RunSignup' for r in rows)} race sites) -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
