#!/usr/bin/env python3
"""build_races.py: builds /san-diego-races/ from data/races.json, data/my-races.json and data/progress.json
(Tyler 2026-11-19: "see what 5ks, 10ks, half marathons, and marathons are in the san diego area ... upcoming ...
select specific dates/distances or search by name. see what i am signed up for").

Every race is written into the HTML (so search engines and AI answers can read the list); the filters are a
small script that only hides rows. "On my plan" marks races on the weekend of a race in progress.json;
"I'm signed up" comes from my-races.json. Run by publish.sh after build_pages.py.

    python3 tools/build_races.py
"""
import datetime as dt
import json
from pathlib import Path

from build_pages import FOOT, FORM, SITE, VER, esc, head

ROOT = Path(__file__).resolve().parents[1]
PATH = "/san-diego-races/"
LABEL = {"5K": "5K", "10K": "10K", "Half": "Half marathon", "Marathon": "Marathon"}
LONG = {"5K": "5K", "10K": "10K", "Half": "half marathon", "Marathon": "marathon"}


def d(s):
    return dt.date.fromisoformat(s)


def weekend(day):
    """The Saturday that starts day's weekend (a Sunday belongs to the Saturday before)."""
    return day - dt.timedelta(days=(day.weekday() - 5) % 7) if day.weekday() >= 5 else None


def nice(day, end=None):
    s = f"{day:%a %b} {day.day}, {day.year}"
    if end and end != day:
        s = f"{day:%a %b} {day.day} to {end:%a %b} {end.day}, {end.year}"
    return s


def clock(t):
    if not t:
        return ""
    h, m = map(int, t.split(":"))
    return f"{(h - 1) % 12 + 1}:{m:02d} {'AM' if h < 12 else 'PM'}"


def main():
    data = json.loads((ROOT / "data" / "races.json").read_text())
    mine = json.loads((ROOT / "data" / "my-races.json").read_text())["races"]
    plan = json.loads((ROOT / "data" / "progress.json").read_text()).get("races", [])
    today = dt.date.today()
    races = [r for r in data["races"] if r["date"] >= today.isoformat()]
    mine_ids = {m["match_id"]: m for m in mine if m.get("match_id")}
    # a race is "on my plan" when it falls on a plan race's weekend AND offers that distance (Chicago itself is not local)
    PLAN_DIST = {"5k": "5K", "10k": "10K", "half marathon": "Half"}
    SHORT = {"5K": "5K", "10K": "10K", "Half": "half marathon"}
    def plan_dist(name):
        """The plan race's distance from its name ("First 5K" -> "5K"); None for Chicago."""
        n = name.lower()
        return next((v for k, v in PLAN_DIST.items() if n == k or n.endswith(" " + k)), None)

    plan_w = {weekend(d(p["date"])): (p["name"], plan_dist(p["name"])) for p in plan
              if weekend(d(p["date"])) and plan_dist(p["name"])}

    # where I'm racing (my entries and the plan's race dates, by date)
    cards = []
    for m in sorted(mine, key=lambda m: m["date"]):
        if m["date"] < today.isoformat():
            continue
        cards.append((m["date"], f'<div class="race{" final" if m.get("goal") else ""}"><div class="d">{esc(nice(d(m["date"])))}</div>'
                     f'<h3>{esc(m["name"])}</h3><div class="k">{esc(m["city"])}</div><p class="rstatus">{esc(m["status"])}</p></div>'))
    for p in plan:
        if p["date"] >= today.isoformat() and not any(m["date"] == p["date"] for m in mine):
            k = plan_dist(p["name"])
            fit = f'<a class="rlink" href="?d={k}&amp;plan=1#rf">See races that fit</a>' if k else ""
            cards.append((p["date"], f'<div class="race open"><div class="d">{esc(nice(d(p["date"])))}</div><h3>My {esc(p["name"])}</h3>'
                         f'<div class="k">Date set by my coach</div><p class="rstatus">Race not picked yet</p>{fit}</div>'))
    cards = [c for _, c in sorted(cards)]

    # the list, grouped by month
    rows, month, ld = [], None, []
    for r in races:
        day, end = d(r["date"]), d(r.get("end") or r["date"])
        if (day.year, day.month) != month:
            if month:
                rows.append("</ol></div>")
            month = (day.year, day.month)
            rows.append(f'<div class="rmonth" data-month="{day:%Y-%m}"><h2 class="display">{day:%B} <span class="o">{day.year}</span></h2><ol class="rlist">')
        w = weekend(day)
        pw = plan_w.get(w) if w else None
        on_plan = SHORT[pw[1]] if pw and pw[1] in r["distances"] else None
        me = mine_ids.get(r["id"])
        tags = "".join(f'<span class="rd">{LABEL[x]}</span>' for x in r["distances"])
        tags += "".join(f'<span class="rd soft">{esc(x)}</span>' for x in r.get("other", []))
        badges = ""
        if me:
            badges += '<span class="rb me">I\'m in</span>'
        if on_plan:
            badges += f'<span class="rb plan">Fits my {esc(on_plan)} date</span>'
        meta = esc(r["city"]) + (f' · {clock(r["start"])} start' if r.get("start") else "")
        link = (f'<a class="rgo" href="{esc(r["url"])}" target="_blank" rel="noopener">Register<span aria-hidden="true"> →</span></a>'
                if r.get("url") else '<span class="rgo off">No link yet</span>')
        name = (f'<a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["name"])}</a>' if r.get("url") else esc(r["name"]))
        rows.append(
            f'<li class="rrow" data-d="{" ".join(r["distances"])}" data-date="{r["date"]}" data-name="{esc(r["name"].lower())}"'
            f' data-plan="{1 if on_plan else 0}" data-mine="{1 if me else 0}">'
            f'<div class="rdate"><span class="dw">{day:%a}</span><span class="dn">{day.day}</span><span class="dm">{day:%b}</span></div>'
            f'<div class="rmain"><h3>{name}</h3><p class="rmeta">{meta}{" · " + esc(nice(day, end)) if end != day else ""}</p>'
            f'<div class="rtags">{tags}{badges}</div>'
            f'<a class="rtrain" href="#show" data-race="{esc(r["name"])} ({day:%b} {day.day})">Training for this one?</a></div>{link}</li>')
        ev = {"@type": "SportsEvent", "name": r["name"], "startDate": r["date"], "endDate": r.get("end") or r["date"],
              "eventStatus": "https://schema.org/EventScheduled", "sport": "Running",
              "location": {"@type": "Place", "name": r["city"],
                           "address": {"@type": "PostalAddress", "addressLocality": r["city"], "addressRegion": "CA", "addressCountry": "US"}}}
        if r.get("url"):
            ev["url"] = r["url"]
        ld.append({"@type": "ListItem", "position": len(ld) + 1, "item": ev})
    if month:
        rows.append("</ol></div>")

    n = len(races)
    counts = {k: sum(k in r["distances"] for r in races) for k in LABEL}
    updated = d(data["updated"])
    title = "San Diego Races: 5K, 10K, Half Marathon and Marathon Calendar | To The Finish"
    desc = (f"{n} upcoming 5Ks, 10Ks, half marathons and marathons within 35 miles of San Diego. "
            "Filter by distance and date or search by name. Updated every Sunday.")
    schema = {"@context": "https://schema.org", "@type": "WebPage", "name": "San Diego races", "url": SITE + PATH,
              "description": desc, "dateModified": data["updated"],
              "mainEntity": {"@type": "ItemList", "name": "Upcoming San Diego races", "numberOfItems": n, "itemListElement": ld}}
    extra = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'

    def when(r):
        x, y = d(r["date"]), d(r.get("end") or r["date"])
        return f"{x:%a %b} {x.day}" + (f" to {y:%a %b} {y.day}" if y != x else "")

    def say(rs):
        rs = [f"{esc(r['name'])} ({when(r)}, {esc(r['city'])})" for r in rs]
        return rs[0] if len(rs) == 1 else ", ".join(rs[:-1]) + " and " + rs[-1]

    def nxt(k, many=5):
        return [r for r in races if k in r["distances"]][:many]

    yr = today.year + 1 if today.month >= 11 else today.year
    halves = [r for r in races if "Half" in r["distances"] and r["date"].startswith(str(yr))]
    by_month = {}
    for r in halves:
        by_month.setdefault(d(r["date"]).strftime("%B"), []).append(r)
    def say_some(rs, k=4):
        if len(rs) <= k:
            return say(rs)
        return ", ".join(f"{esc(r['name'])} ({when(r)}, {esc(r['city'])})" for r in rs[:k]) + f" and {len(rs) - k} more"
    month_lines = "".join(f"<li><b>{m}:</b> {say_some(rs)}.</li>" for m, rs in by_month.items())
    last = d(races[-1]["date"]) if races else today
    QA = [
        ("What are the next half marathons in San Diego?", f"The next ones are {say(nxt('Half'))}."),
        (f"Which half marathons are in San Diego in {yr}?", f"<ul>{month_lines}</ul>" if month_lines else "None are posted yet."),
        ("What 5K races are coming up in San Diego?", f"The next 5Ks are {say(nxt('5K'))}."),
        ("What 10K races are coming up in San Diego?", f"The next 10Ks are {say(nxt('10K'))}."),
        ("Are there marathons in San Diego?", f"{len(nxt('Marathon', 10))} on the list right now: {say(nxt('Marathon', 10))}." if nxt('Marathon') else "None are posted yet."),
        ("How many races are on this list?", f"{n} races between now and {last:%B} {last.year}: {counts['5K']} with a 5K, {counts['10K']} with a 10K, "
                                             f"{counts['Half']} with a half marathon and {counts['Marathon']} with a marathon. Many races offer more than one distance."),
    ]
    QA_HTML = "".join(f"<h3>{q}</h3>" + (a if a.startswith("<ul>") else f"<p>{a}</p>") for q, a in QA)

    # paid-link disclosure whenever the RunSignup links carry the affiliate token (voice gate: disclose paid links)
    AFFILIATE = ("If you register through a RunSignup link here, RunSignup shares a small part of its fee with me. "
                 if any("aflt_token=" in (r.get("url") or "") for r in races) else "")
    # what the show is: point at the episodes once one is out
    eps = json.loads((ROOT / "episodes" / "episodes.json").read_text()) if (ROOT / "episodes" / "episodes.json").exists() else []
    SHOW_NEXT = ('<a href="/episodes/">Watch the episodes</a>.' if eps
                 else "Episode 1 comes out Sunday, Nov 22.")
    # race picker (Tyler 2026-11-20, from the race-finder research: "what race are you training for?"): a select built from
    # the list, sent to the same Kit form in the training_for field it already had; "Something else" opens a text box
    # (CSS :has) and join.js folds the typed race into the same field. GA4 gets the pick as race_pick.
    groups, gm = [], None
    for r in races:
        day = d(r["date"])
        if (day.year, day.month) != gm:
            gm = (day.year, day.month)
            groups.append([f"{day:%B} {day.year}", []])
        v = f'{r["name"]} ({day:%b} {day.day})'
        groups[-1][1].append(f'<option value="{esc(v)}">{esc(r["name"])} · {day:%a %b} {day.day}</option>')
    OPTS = "".join(f'<optgroup label="{g}">{"".join(o)}</optgroup>' for g, o in groups)
    OPTS += ('<optgroup label="Further away"><option value="Chicago Marathon (Oct 10, 2027)">Chicago Marathon · Sun Oct 10, 2027</option></optgroup>'
             '<option class="else" value="Something else">Something else</option>')

    def picker(fid, thanks):
        return f"""<form class="join" action="https://app.kit.com/forms/10209840/subscriptions" method="post" id="join-{fid}" data-thanks="thanks-{fid}">
      <input name="fields[first_name]" aria-label="First name" placeholder="First name" autocomplete="given-name">
      <input name="email_address" type="email" aria-label="Email" placeholder="Email" required autocomplete="email">
      <select id="race-{fid}" name="fields[training_for]" aria-label="What race are you training for?"><option value="">Pick your race</option>{OPTS}</select>
      <input class="wide other" aria-label="Your race and date" placeholder="Your race and date">
      <button type="submit">Get on the list</button>
    </form>
    <div class="thanks" id="thanks-{fid}">{thanks}</div>"""

    WAITLIST_FORM = picker("races", "You're on the list. Good luck with your race.") + """
    <p class="fine">You'll also get my Sunday email: my week's miles and the new episode. It's free, and you can unsubscribe anytime.</p>"""
    PICK_FORM = picker("pick", "You're on the list. Good luck with your race.")
    html = head(title, desc, PATH, extra) + f"""    <div class="page">
      <p class="kicker">San Diego races · Updated {updated:%b} {updated.day}, {updated.year}</p>
      <h1 class="display">San Diego <span class="o">races.</span></h1>
      <p class="lead">Every 5K, 10K, half marathon and marathon within 35 miles of San Diego, in one list. Pick a distance and dates, or search by name. It updates every Sunday.</p>
      <p class="body">I'm Tyler, and I'm training for a sub-3 marathon in Chicago with five AI coaches on my show, <a href="#show">To The Finish</a>. I use this list to pick my own races, so the ones I'm running are marked. <a href="#mine">See where I'm racing</a>.</p>
      <p class="kicker" id="pick" style="margin-top:34px">What race are you training for?</p>
      <p class="body">Right now my coaches have one runner: me. If they get me to Chicago, this list tries them next, and I'll know whose races I'm building for.</p>
      {PICK_FORM}
    </div>
  </div>
</header>
<section class="finder">
  <div class="wrap">
    <form class="rfilters" id="rf" role="search" onsubmit="return false">
      <input type="search" id="rq" placeholder="Search by race name" aria-label="Search by race name" autocomplete="off">
      <div class="rgroup" role="group" aria-label="Distance">
        <span class="rlab">Distance</span>
        {"".join(f'<button type="button" class="chip" data-dist="{k}" aria-pressed="false">{LABEL[k]} <span class="cnt">{counts[k]}</span></button>' for k in LABEL)}
      </div>
      <div class="rgroup" role="group" aria-label="When">
        <span class="rlab">When</span>
        <button type="button" class="chip" data-when="30" aria-pressed="false">Next 30 days</button>
        <button type="button" class="chip" data-when="90" aria-pressed="false">Next 3 months</button>
        <button type="button" class="chip" data-when="all" aria-pressed="true">All</button>
        <label class="rdates"><span>From</span><input type="date" id="rfrom" min="{today}"></label>
        <label class="rdates"><span>To</span><input type="date" id="rto" min="{today}"></label>
      </div>
      <div class="rgroup" role="group" aria-label="My races">
        <span class="rlab">My races</span>
        <button type="button" class="chip" data-flag="mine" aria-pressed="false">Races I'm in</button>
        <button type="button" class="chip" data-flag="plan" aria-pressed="false">Fits my race dates</button>
      </div>
      <p class="rhelp"><span class="rb me">I'm in</span> I signed up for it. <span class="rb plan">Fits my 10K date</span> It falls on a weekend my coach set for one of my races, at that distance.</p>
    </form>
    <p class="rcount" aria-live="polite"><b id="rn">{n}</b> <span id="rnl">races</span> <button type="button" class="rclear" id="rclear" hidden>Clear filters</button></p>
    <div id="rall">{"".join(rows)}</div>
    <p class="rempty" id="rempty" hidden>No races match. Try more dates or another distance.</p>
    <p class="note">Listings come from RunSignup and the races' own sites, checked {updated:%b} {updated.day}, {updated.year}. Dates change, so check the race's page before you register. {AFFILIATE}Know a San Diego race I missed? <a href="mailto:hello@tothefinish.ai">hello@tothefinish.ai</a></p>
  </div>
</section>
<section class="answers">
  <div class="wrap prose">
    <p class="kicker">Quick answers</p>
    <h2 class="display sec">San Diego races, <span class="o">at a glance.</span></h2>
    {QA_HTML}
    <p class="note">Built from the list above, updated {updated:%b} {updated.day}, {updated.year}. Check each race's page before you register.</p>
  </div>
</section>
<section class="sunday" id="show">
  <div class="wrap">
    <p class="kicker">Got a race coming up?</p>
    <h2 class="display">Want AI coaches <span class="o">for your race?</span></h2>
    <p class="body">To The Finish is my YouTube show about chasing a sub-3 marathon at Chicago on October 10, 2027. Five AI coaches see everything my watch sees and argue about my week like it's theirs. {SHOW_NEXT}</p>
    <p class="body">Right now they coach one runner: me. If they get me to Chicago, the people on this list are next. Tell me your race so I know who I'm building it for.</p>
    {WAITLIST_FORM}
  </div>
</section>
<section class="mine" id="mine">
  <div class="wrap">
    <p class="kicker">Where I'm racing</p>
    <h2 class="display">My race <span class="o">calendar.</span></h2>
    <p class="body">My AI running coach, Kai, set the dates on the way to Chicago. I pick the races that fill them.</p>
    <div class="rgrid">{"".join(cards)}</div>
    <p class="body" style="margin-top:22px"><a href="/races/">My race reports and Kai's targets</a></p>
  </div>
</section>
<script src="/assets/races.js?v={VER}" defer></script>
{FOOT}"""
    out = ROOT / "san-diego-races"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html)
    print(f"built san-diego-races ({n} races, {len(cards)} on my list)")


if __name__ == "__main__":
    main()
