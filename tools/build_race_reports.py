#!/usr/bin/env python3
"""build_race_reports.py: my race pages, built from data/progress.json (Tyler 2026-11-20: "do ... a page for each San Diego
race"; the race-finder research said build pages for the races I actually run, with Kai's take and my Garmin data,
not one thin page per listed race).

  /races/              the races on my plan: Kai's target and Garmin's prediction for the ones ahead, a link to the
                       report for each one I've run
  /races/<date>-<name>/  one report per race with a `result` block: watch time against the target, mile splits,
                       heart rate, the course (Kai's ground read), Kai's take, what changed after, the next race

The `result` blocks come from the Brain's scripts/site_progress.py (Garmin run on the race date; miles, times, feet and
heart rates only, no GPS). A report appears on its own the first time progress.json carries a result: the Sunday
refresh or any publish. Run by publish.sh after build_chicago.py.

    python3 tools/build_race_reports.py [--data data/progress.json] [--out DIR]   # --out: render somewhere else (tests)
"""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

from build_pages import FOOT, FORM, SITE, esc, head

ROOT = Path(__file__).resolve().parents[1]


def d(s):
    return dt.date.fromisoformat(s)


def nice(day):
    return f"{day:%a %b} {day.day}, {day.year}"


def slug(r):
    name = re.sub(r"^first\s+", "", r["name"].lower())
    return f'{r["date"]}-{re.sub(r"[^a-z0-9]+", "-", name).strip("-")}'


def short(name):
    """'First 5K' -> '5K', 'Half marathon' -> 'half marathon' (for sentences)."""
    n = re.sub(r"^First\s+", "", name)
    return n if "Chicago" in n or n.upper().endswith("K") else n.lower()


def report_urls(prog):
    """[(path, lastmod)] for the sitemap: the index and every race with a result."""
    out = [("/races/", prog["updated"])]
    out += [(f"/races/{slug(r)}/", r["date"]) for r in prog.get("races", []) if r.get("result")]
    return out


def mine_on(day):
    """My entry on that date from data/my-races.json (the race's real name and city), if I picked one."""
    try:
        mine = json.loads((ROOT / "data" / "my-races.json").read_text())["races"]
    except Exception:  # noqa: BLE001
        return None
    return next((m for m in mine if m["date"] == day), None)


def table(head_row, rows):
    th = "".join(f'<th scope="col">{esc(c)}</th>' for c in head_row)
    tb = "".join("<tr>" + "".join(f'<td data-label="{esc(h)}">{esc(str(c))}</td>' for h, c in zip(head_row, r)) + "</tr>"
                 for r in rows)
    return f'<div class="tablewrap"><table class="qt"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>'


def updown(u, dn):
    if u is None and dn is None:
        return ""
    return f"+{u or 0} / {'-' + str(dn) if dn else '0'} ft"


def hr(a, b):
    if not a:
        return ""
    return f"{a} / {b}" if b else f"{a}"


def report_page(r, nxt, prog):
    res = r["result"]
    path = f"/races/{slug(r)}/"
    day = d(r["date"])
    me = mine_on(r["date"])
    event = me["name"] if me else f"My {short(r['name'])}"
    target = r.get("target") or r.get("goal")
    title = f"{event}, {nice(day)}: {res['time']} race report | To The Finish"
    desc = (f"My {short(r['name'])} on {nice(day)}: {res['time']} on my Garmin"
            + (f" against Kai's target of {target}" if target else "")
            + ". Mile splits, heart rate, the course and what my AI running coach changed after.")
    if "Chicago" in r["name"]:
        h1 = 'Chicago <span class="o">Marathon.</span>'
    else:
        h1 = f'My <span class="o">{esc(short(r["name"]))}.</span>'

    # structured data: the article, about the race (a SportsEvent only when I ran a named race with a city)
    art = {"@context": "https://schema.org", "@type": "Article", "headline": title[:110], "description": desc,
           "author": {"@type": "Person", "name": "Tyler Stewart", "url": SITE + "/ai-running-coach/"},
           "datePublished": f'{r["date"]}T18:00:00-08:00', "dateModified": f'{prog["updated"]}T18:00:00-08:00',
           "publisher": {"@type": "Organization", "name": "To The Finish", "url": SITE + "/",
                         "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo.png"}},
           "mainEntityOfPage": SITE + path}
    if me and me.get("city"):
        art["about"] = {"@type": "SportsEvent", "name": me["name"], "startDate": r["date"], "sport": "Running",
                        "eventStatus": "https://schema.org/EventScheduled",
                        "location": {"@type": "Place", "name": me["city"],
                                     "address": {"@type": "PostalAddress", "addressLocality": me["city"], "addressCountry": "US"}}}
    extra = f'<script type="application/ld+json">{json.dumps(art, ensure_ascii=False)}</script>'

    # the numbers at a glance
    facts = [("My watch", res["time"], f'{res["dist_mi"]} mi')]
    if target:
        facts.append(("Kai's target" if r.get("target") else "Goal", target, "Set before the race"))
    facts.append(("Pace", f'{res["pace"]}', "Per mile"))
    if res.get("hr"):
        facts.append(("Heart rate", str(res["hr"]), f'Average · peak {res["peak"]}' if res.get("peak") else "Average"))
    if res.get("up_ft") is not None:
        facts.append(("Climbing", f'+{res["up_ft"]} ft', f'-{res.get("down_ft") or 0} ft down'))
    if res.get("temp_f"):
        facts.append(("Start", f'{res["temp_f"]}°F', "At the start"))
    facts_html = "".join(f'<div><span class="k">{esc(k)}</span><b>{esc(v)}</b><span>{esc(s)}</span></div>' for k, v, s in facts)

    if res.get("how") == "whole run":
        how = "The time is the whole run on my Garmin, start to stop."
    elif res.get("how") == "race lap":
        how = "The time is the race lap on my Garmin; the warm-up was on the same file."
    else:
        how = f"The time is Garmin's best {short(r['name'])} inside a longer run, so there are no splits for it."

    kai = "".join(f"<p>{esc(x)}</p>" for x in res.get("kai") or [])
    kai_html = (f'<blockquote class="say"><img src="/assets/kai.jpg" alt="" width="48" height="48"><div>{kai}<cite>Kai</cite></div></blockquote>'
                if kai else "")

    # splits + heart rate by mile
    splits = res.get("splits") or []
    if splits:
        rows = []
        for i, s in enumerate(splits, 1):
            label = f"Mile {i}" if s["dist_mi"] >= 0.95 else f"Last {s['dist_mi']:.2f} mi"
            rows.append((label, s["time"], s["pace"], hr(s.get("hr"), s.get("peak")), updown(s.get("up_ft"), s.get("down_ft"))))
        splits_html = table(("Split", "Time", "Pace / mi", "Heart rate (avg / peak)", "Up / down"), rows)
    else:
        splits_html = '<p class="body">No mile splits for this one. The watch only has the race as one piece.</p>'

    # the course: Kai's ground read when there is one, else the watch's feet per mile
    course = res.get("course") or []
    if course:
        climbs = [c for c in course if c["ground"] == "Climb"]
        big = max(climbs, key=lambda c: c["up_ft"] or 0) if climbs else None
        lead = (f'The biggest climb was miles {esc(big["miles"])}: +{big["up_ft"]} ft in {esc(big["time"] or "")}, heart rate {big["hr"]} going up.'
                if big and big.get("hr") else
                "No real climbs on this course. Kai read it as rolling ground the whole way.")
        course_html = (f'<p class="body">{lead}</p>'
                       + table(("Miles", "Ground", "Up / down", "Time", "Heart rate (avg / peak)"),
                               [(c["miles"], c["ground"], updown(c["up_ft"], c["down_ft"]), c["time"] or "", hr(c["hr"], c["peak"]))
                                for c in course]))
    elif res.get("up_ft") is not None:
        course_html = (f'<p class="body">+{res["up_ft"]} ft up and -{res.get("down_ft") or 0} ft down on my watch. '
                       "Kai's read of the ground didn't come through for this one, so the feet per mile are in the splits above.</p>")
    else:
        course_html = '<p class="body">No course data on this file.</p>'

    after = res.get("after")
    if after and after.get("threshold_before"):
        after_html = (f'<p class="body">Kai re-set my threshold pace off this race: {esc(after["threshold_before"])} a mile before it, '
                      f'{esc(after["threshold_after"])} after. Every threshold rep from here runs off the new number.</p>')
    elif after:
        after_html = (f'<p class="body">Kai set my threshold pace off this race: {esc(after["threshold_after"])} a mile. '
                      "Every threshold rep from here runs off it.</p>")
    else:
        after_html = ('<p class="body">Nothing has moved yet. My paces re-set from Garmin after every sync, '
                      "and this page changes with them.</p>")

    if nxt:
        nd = d(nxt["date"])
        tgt = nxt.get("target") or nxt.get("goal")
        lab = "Kai's target" if nxt.get("target") else "Goal"
        next_html = (f'<div class="rgrid" style="max-width:340px"><div class="race{" final" if nxt.get("goal") else ""}"><div class="d">{esc(nice(nd))}</div>'
                     f'<h3>{esc(nxt["name"])}</h3><div class="k">{lab}</div><div class="v o">{esc(tgt or "")}</div>'
                     f'<div class="k">Watch says today</div><div class="v">{esc(nxt.get("today") or "")}</div></div></div>')
    else:
        next_html = ""

    return head(title, desc, path, extra) + f"""    <div class="page">
      <p class="kicker">Race report · {esc(nice(day))}</p>
      <h1 class="display">{h1}</h1>
      <p class="lead">{esc(me["name"] + ", " + me["city"] + ". ") if me else ""}{esc(res["time"])} on my watch{", and Kai's target was " + esc(target) if target else ""}. Here's every mile of it.</p>
    </div>
  </div>
</header>
<section class="glance">
  <div class="wrap">
    <p class="kicker">The race</p>
    <div class="facts">{facts_html}</div>
    {kai_html}
    <p class="note" style="margin-top:14px">{esc(how)} Watch time, not the official result.</p>
  </div>
</section>
<section>
  <div class="wrap prose">
    <p class="kicker">Mile by mile</p>
    <h2 class="display sec">The <span class="o">splits.</span></h2>
    {splits_html}
    <h2>The course</h2>
    {course_html}
    <h2>What changed after</h2>
    {after_html}
  </div>
</section>
<section class="mine">
  <div class="wrap">
    <p class="kicker">Next</p>
    <h2 class="display sec">The next <span class="o">race.</span></h2>
    {next_html}
    <p class="body" style="margin-top:22px"><a href="/races/">All my races</a> · <a href="/chicago-marathon-2027/">Chicago 2027</a></p>
  </div>
</section>
<section class="sunday">
  <div class="wrap">
    <p class="kicker">The next chapter</p>
    <h2 class="display">Sunday is <span class="o">the long run.</span></h2>
    {FORM.format(id='race', button='Get the Sunday letter')}
    <p class="note" style="margin-top:18px">Numbers from my Garmin (chest-strap heart rate). Not medical advice; the coaches are AI characters.</p>
  </div>
</section>
""" + FOOT


def index_page(prog):
    path = "/races/"
    today = dt.date.today().isoformat()
    races = prog.get("races", [])
    done = [r for r in races if r.get("result")]
    ahead = [r for r in races if not r.get("result") and r["date"] >= today]
    n = len(races)
    desc = ("My races on the way to a sub-3 marathon at Chicago on October 10, 2027: Kai's target for each one, Garmin's "
            "prediction today, and a race report with splits and heart rate after every race I run.")

    def card(r):
        day = d(r["date"])
        tgt = r.get("target") or r.get("goal")
        lab = "Kai's target" if r.get("target") else "Goal"
        h = f'<div class="race{" final" if r.get("goal") else ""}"><div class="d">{esc(nice(day))}</div><h3>{esc(r["name"])}</h3>'
        if r.get("result"):
            h += (f'<div class="k">My watch</div><div class="v">{esc(r["result"]["time"])}</div>'
                  f'<div class="k">{lab}</div><div class="v o">{esc(tgt or "")}</div>'
                  f'<a class="rlink" href="/races/{slug(r)}/">Race report</a>')
        else:
            h += (f'<div class="k">{lab}</div><div class="v o">{esc(tgt or "")}</div>'
                  f'<div class="k">Watch says today</div><div class="v">{esc(r.get("today") or "")}</div>')
        return h + "</div>"

    items = []
    for i, r in enumerate(done + ahead):
        it = {"@type": "ListItem", "position": i + 1, "name": f'{r["name"]}, {nice(d(r["date"]))}'}
        if r.get("result"):
            it["url"] = f"{SITE}/races/{slug(r)}/"
        items.append(it)
    schema = {"@context": "https://schema.org", "@type": "WebPage", "name": "My races | To The Finish", "url": SITE + path,
              "description": desc, "dateModified": prog["updated"],
              "mainEntity": {"@type": "ItemList", "name": "My races to Chicago 2027", "numberOfItems": len(items),
                             "itemListElement": items}}
    extra = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'

    first = ahead[0] if ahead else None
    if done:
        done_html = f'<div class="rgrid">{"".join(card(r) for r in reversed(done))}</div>'
    else:
        when = f"{d(first['date']):%A, %B} {d(first['date']).day}" if first else "after the first race"
        done_html = f'<p class="body">None yet. The first one is {esc(when)}, and the report goes up here after it.</p>'
    ahead_html = f'<div class="rgrid">{"".join(card(r) for r in ahead)}</div>' if ahead else ""
    upd = d(prog["updated"])

    return head("My Races: Targets and Race Reports on the Way to a Sub-3 Chicago | To The Finish", desc, path, extra) + f"""    <div class="page">
      <p class="kicker">My races · Updated {upd:%b} {upd.day}, {upd.year}</p>
      <h1 class="display">My <span class="o">races.</span></h1>
      <p class="lead">{n} races between now and Chicago on October 10, 2027. Kai set the dates and the targets. After each one, the splits and the heart rate go up here, straight off my watch.</p>
    </div>
  </div>
</header>
<section class="mine">
  <div class="wrap">
    <p class="kicker">Coming up</p>
    <h2 class="display sec">The races <span class="o">ahead.</span></h2>
    {ahead_html}
    <p class="note" style="margin-top:14px">"Watch says today" is Garmin's prediction if I raced today. "Kai's target" is the time that keeps sub-3 on track at that point in the year.</p>
  </div>
</section>
<section>
  <div class="wrap">
    <p class="kicker">Race reports</p>
    <h2 class="display sec">The races <span class="o">I've run.</span></h2>
    {done_html}
    <p class="body" style="margin-top:22px"><a href="/san-diego-races/">The San Diego races I pick from</a> · <a href="/chicago-marathon-2027/">Chicago 2027</a></p>
  </div>
</section>
<section class="sunday">
  <div class="wrap">
    <p class="kicker">What are you training for?</p>
    <h2 class="display">Your race, <span class="o">next.</span></h2>
    <p class="body">Right now my coaches have one runner: me. If they get me to Chicago, the people on this list are next. Tell me your race.</p>
    <form class="join" id="join-myraces" data-thanks="thanks-myraces">
      <input name="fields[first_name]" aria-label="First name" placeholder="First name" autocomplete="given-name">
      <input name="email_address" type="email" aria-label="Email" placeholder="Email" required autocomplete="email">
      <input class="wide" name="fields[training_for]" aria-label="Your race and date" placeholder="Your race and date">
      <button type="submit">Get on the list</button>
    </form>
    <div class="thanks" id="thanks-myraces">You're on the list. Good luck with your race.</div>
    <p class="fine">You'll also get my Sunday letter: my week's miles and the new episode. It's free, and you can unsubscribe anytime.</p>
  </div>
</section>
""" + FOOT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "progress.json"))
    ap.add_argument("--out", default=str(ROOT))
    a = ap.parse_args()
    prog = json.loads(Path(a.data).read_text())
    out = Path(a.out) / "races"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(index_page(prog))
    races = prog.get("races", [])
    n = 0
    for i, r in enumerate(races):
        if not r.get("result"):
            continue
        nxt = next((x for x in races[i + 1:] if not x.get("result")), None)
        p = out / slug(r)
        p.mkdir(parents=True, exist_ok=True)
        (p / "index.html").write_text(report_page(r, nxt, prog))
        n += 1
    print(f"built races index ({len(races)} races) and {n} race report(s)")


if __name__ == "__main__":
    main()
