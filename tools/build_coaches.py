#!/usr/bin/env python3
"""Build /coaches/: what each AI coach watches, what they do with it, and the numbers they're watching now.

Tyler 2026-11-21: "redesign the charts for a coaches page". The homepage stays short; this page carries the charts,
drawn by assets/charts.js (one chart system) from data/progress.json via assets/coaches-page.js. Header, footer
and type come from the homepage so both pages read as one site. Re-run by tools/publish.sh.

2026-11-21, Sanderson full read (people before systems): each coach now opens with their own line on this week's
numbers, then what they do and the one thing they can't, then the charts. The study and work counts sit in one line at
the foot. One Sunday letter ask on the page, at the end. 2026-11-21 evening: the waitlist and the per-coach interest
links are gone (Tyler: "take down waitlist and make the Sunday letter the only sign up"; trademark read in the Brain,
brain/business/to-the-finish/name-check-2026-11-21.md).

2026-11-22, the data (Tyler: "let's really nerd out on all the data that my coaches see ... make clear it's all built off
this real data, and show how much data we're really collecting, and show the charts"): a first section that draws one whole
run, one minute of heartbeats and every run since 2024, then under each coach every number that coach reads, with its last
values. All of it comes from data/feed.json (the brain's scripts/site_feed.py counts every number; nothing is typed here).
His word puts the counts up front, over the story-voice rule that counts never lead (W8, K4).
"""
import json
import re
from pathlib import Path

from build_pages import site_footer, site_nav   # one nav and one footer for every page (read from index.html)

ROOT = Path(__file__).resolve().parents[1]

COACHES = [
    dict(k="kai", n="Kai", role="AI running coach", live="runs analyzed",
         watch=["Every lap and split", "Heart rate from a chest strap", "Hills and grade", "Heat and weather",
                "Threshold pace", "Race results"],
         does=("Builds the year race by race, a 5K, a 10K, a half, then the marathon, and sets every pace and "
               "heart-rate zone from my own runs. A slow mile up a climb gets credit for the faster flat mile it "
               "took the same effort to run. He can't make me run an easy day easy. The watch shows the range and "
               "the rest is mine."),
         charts=[("engine", "Is the engine coming back?",
                  "Lactate-threshold pace from my Garmin: about the fastest I can hold for an hour. Higher is faster."),
                 ("eff", "Am I fitter at the same heart rate?",
                  "Meters I travel for each heartbeat on easy runs, four-week average, hills evened out. Higher is fitter."),
                 ("miles", "Am I running the miles?",
                  "Planned miles each week from now to Chicago, and the miles I ran.",
                  [("muted", "Ran"), ("ghost", "Planned"), ("orange", "This week")]),
                 ("zones", "How hard was every minute?",
                  "Minutes in each heart-rate zone, week by week. The watch sorts every second into one of five.",
                  [("z1", "1"), ("z2", "2"), ("z3", "3"), ("z4", "4"), ("z5", "5")]),
                 ("form", "What is my stride doing?",
                  "Weekly averages from every run since May 2024. The big numbers are this week.")],
         line="kai_year"),
    dict(k="mo", n="Mo", role="AI recovery coach", live="nights of sleep analyzed",
         watch=["Hours asleep", "Resting heart rate", "Overnight heart rhythm (HRV)", "Every run's length",
                "Easy-day heart rate", "My legs and pain check-ins"],
         does=("Reads my sleep and resting heart rate, and they can only ever make a day easier. Checks every run "
               "against my longest of the last 30 days, because a big jump past it is linked to more injuries, and builds the warm-ups, the foot and ankle work and the "
               "lighter weeks around the plan. He can't see pain. I have to tell him."),
         charts=[("easy", "Are the easy days easy?",
                  "Share of each week's running time at easy heart rate. The best distance "
                  "runners keep at least 80% easy."),
                 ("sleep", "Am I sleeping enough?",
                  "Hours asleep each night from my watch. Watches count broken nights long, so those bars are faded.",
                  [("orange", "7 hours or more"), ("muted", "Under 7"), ("dim", "Broken night")]),
                 ("stages", "What kind of sleep was it?",
                  "Hours in each stage, the last 30 nights the watch recorded.",
                  [("orange", "Deep"), ("white", "REM"), ("muted", "Light"), ("z1", "Awake")]),
                 ("hrv", "Is my heart's rhythm in its normal range?",
                  "Overnight HRV, the tiny differences between one heartbeat and the next. The gray band is the range the watch "
                  "has worked out for me. The holes are nights I slept without it."),
                 ("rhr", "Is my resting heart rate climbing?",
                  "One number for each night I wore the watch, all year. A week at three percent over its usual, with a second bad sign beside it, turns a hard day easy."),
                 ("load", "How much work is in my legs?",
                  "Training load from the watch, the last seven days added up."),
                 ("spike", "Did any run jump too far?",
                  "Minutes in each run. The dashed line is Mo's ceiling that day: a tenth past the longest run of the 30 days before. Red is over it.")],
         line="mo_sleep"),
    dict(k="bo", n="Bo", role="AI strength coach", live="lifts tracked",
         watch=["The heaviest set I text after each lift", "The run calendar", "Which days carry a hard run"],
         does=("Heavy sets of three and jumps, the strength work that makes runners faster, fitted around the run "
               "and never the other way around. Sets my next weights from my last heaviest sets. He can't see a "
               "lift. He knows what I text him."),
         charts=[], line="bo"),
    dict(k="juno", n="Juno", role="AI nutritionist", live="foods measured",
         watch=["Today's and tomorrow's run", "The food in the house", "Grocery receipts and fridge photos",
                "The meals on the plan", "My 7-day weigh-in trend"],
         does=("Writes my food every day from the run it has to fuel and what's in the house. A photo of a receipt "
               "or the fridge updates what's there. She checks my 7-day weigh-in trend against the work ahead. "
               "As the running grows, she feeds more of it. She can't change a food rule without my word."),
         charts=[("fuel", "Does the food follow the work?",
                  "Grams of carbs a day from my meal plan, the next seven days.",
                  [("orange", "Hard or long run"), ("muted", "Easy or rest day")])],
         line="juno"),
    dict(k="rook", n="Rook", role="AI head coach", live="decisions made",
         watch=["Every coach's plan", "The priority board", "Every call the coaches make", "What I tell the coaches"],
         does=("Settles every clash between the coaches: what I say and any pain first, then Chicago, then weight, "
               "then strength. Tracks the gap to sub-3 every morning and writes down every decision the team makes. "
               "What I say outranks every number he has."),
         charts=[("gap", "Am I closing the gap?",
                  "Garmin's marathon prediction after every run since October 19, against my sub-3 goal for Chicago."),
                 ("calls", "Who makes the calls?",
                  "Every decision the coaches wrote down since Nov 9, by the coach who made it.",
                  [("orange", "Automatic, from watch data"), ("white", "A coach's own call"), ("muted", "I overruled it")])],
         line="rook"),
]

CSS = """<style>
.intro{padding:24px 0 40px}
.intro h1{font-size:clamp(52px,8vw,104px)}
.intro .lead{font-size:20px;line-height:1.5;color:var(--soft);max-width:52ch;margin:20px 0 0;text-wrap:pretty}
.jumpbar{position:sticky;top:0;z-index:30;background:rgba(18,16,14,.92);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.jump{display:flex;gap:8px;padding:10px 0;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.jump::-webkit-scrollbar{display:none}
.jump a{flex:none;display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 16px 0 7px;border:1px solid var(--line);border-radius:999px;text-decoration:none;font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;text-transform:uppercase;letter-spacing:1px;font-size:17px;color:var(--soft);background:var(--ink-2);transition:border-color .15s,color .15s}
.jump a:hover{border-color:var(--orange)}
.jump a.jd{padding:0 16px}
.jump a[aria-current]{border-color:var(--orange);color:#fff;background:#2b1a0f}
.jump img{width:30px;height:30px;border-radius:50%;object-fit:cover}
.cs{scroll-margin-top:64px}
.cs{padding:80px 0}
.ch{display:grid;grid-template-columns:148px 1fr;gap:0 28px;align-items:start}
.ch img{grid-row:1/span 3;width:148px;height:185px;object-fit:cover;object-position:50% 20%;border-radius:14px;border:1px solid var(--line)}
.ch h2{font-size:clamp(48px,6vw,72px)}
.ch .kicker{margin-bottom:8px}
.ch .proof{margin:12px 0 0;font-size:15px;color:var(--muted)}
.ch .proof b{color:var(--orange);font-weight:700}
.ch .does{margin:14px 0 0;font-size:18px;line-height:1.55;color:var(--soft);max-width:62ch;text-wrap:pretty}
.ch .does,.ch .tags{grid-column:2}
.tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.tags span{padding:5px 11px;border-radius:999px;border:1px solid #4a433c;font-size:14px;color:#e7e2dc}
.vizgrid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:40px}
.viz{display:grid;grid-template-rows:subgrid;grid-row:span 3;row-gap:0}
.vizgrid.one{grid-template-columns:1fr}
.viz{margin:0;background:var(--ink-2);border:1px solid var(--line);border-radius:16px;padding:22px 22px 18px;min-width:0}
.viz.wide{grid-column:1/-1}
.viz .q{margin:0;font-size:14px;font-weight:600;color:var(--muted)}
.viz .take{text-wrap:balance;margin:6px 0 18px;font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;text-transform:uppercase;font-size:30px;line-height:1.05}
.viz .take b{color:var(--orange);font-weight:800}
.viz .take span{display:block;margin-top:4px;font-size:20px;color:var(--muted)}
.plot{width:100%;min-height:200px}
.src{margin:14px 0 0;font-size:14px;line-height:1.5;color:var(--muted);align-self:end}
.key{display:flex;flex-wrap:wrap;gap:6px 16px;margin:-6px 0 14px;font-size:14px;color:var(--soft)}
.key span{display:inline-flex;align-items:center;gap:7px}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px}
.sw.orange{background:#ff6a1f}.sw.white{background:#fff}.sw.muted{background:#5f5750}.sw.dim{background:#5f5750;opacity:.55}.sw.ghost{border:1.5px solid #6b625a}
.lifts{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.lift{background:var(--ink-2);border:1px solid var(--line);border-radius:14px;padding:22px}
.lift .n{font-size:14px;font-weight:600;color:var(--muted);margin:0}
.lift .v{font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;font-size:56px;line-height:1;margin:8px 0 0}
.lift .v small{font-size:.4em;color:var(--muted);margin-left:4px}
.lift .s{font-size:14px;color:var(--soft);margin:10px 0 0}
.say{display:flex;gap:14px;align-items:center;margin:16px 0 0;padding:16px 20px;background:var(--ink-2);border-left:4px solid var(--orange);border-radius:14px}
.ask{display:flex;align-items:center;justify-content:space-between;gap:12px 24px;flex-wrap:wrap;margin:12px 0 0;padding:12px 12px 12px 20px;border:1px solid var(--line);border-radius:14px}
.ask p{margin:0;font-size:17px;line-height:1.45;color:var(--soft)}
.ask a{flex:none;display:inline-flex;align-items:center;min-height:44px;padding:0 20px;border:1.5px solid var(--orange);border-radius:10px;color:var(--orange);text-decoration:none;font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;text-transform:uppercase;letter-spacing:1px;font-size:17px;transition:background .15s,color .15s}
.ask a:hover{background:var(--orange);color:#12100e}
.say img{width:44px;height:44px;border-radius:50%;object-fit:cover;flex:none}
.say p{margin:0;font-size:17px;line-height:1.5;text-wrap:pretty}
.sw.z1{background:#4d463f}.sw.z2{background:#7a7068}.sw.z3{background:#c48a63}.sw.z4{background:#ff6a1f}.sw.z5{background:#fff}
/* the data */
.feed{scroll-margin-top:64px;padding:80px 0}
.feed h2{font-size:clamp(48px,8vw,104px);max-width:14ch}
.counts{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;margin:44px 0 0;background:var(--line);border:1px solid var(--line);border-radius:16px;overflow:hidden}
.counts div{background:var(--ink-2);padding:20px 20px 18px}
.counts b{display:block;font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;font-size:46px;line-height:1;font-variant-numeric:tabular-nums}
.counts div:first-child b{color:var(--orange)}
.counts span{display:block;margin-top:8px;font-size:15px;line-height:1.35;color:var(--soft)}
.feed .viz,.feed .vizgrid .viz{display:block}
.feed .viz{margin-top:16px}
.feed .vizgrid{margin-top:16px}.feed .vizgrid .viz{margin-top:0}
.scrub{display:block;width:100%;height:44px;margin:4px 0 0;accent-color:var(--orange);cursor:ew-resize}
.tip{min-height:22px;margin:10px 0 0;font-size:15px;color:#fff;font-weight:600}
.path{list-style:none;margin:44px 0 0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:16px;counter-reset:st}
.path li{counter-increment:st;background:var(--ink-2);border:1px solid var(--line);border-radius:14px;padding:20px}
.path li::before{content:counter(st);font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;font-size:18px;color:var(--orange)}
.path b{display:block;margin-top:6px;font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;text-transform:uppercase;font-size:26px;line-height:1.05}
.path span{display:block;margin-top:8px;font-size:16px;line-height:1.45;color:var(--soft)}
.feed h3,.nh{font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;text-transform:uppercase;font-size:34px;line-height:1.05;margin:56px 0 0}
.feed h3+p{margin:10px 0 0;font-size:17px;line-height:1.5;color:var(--soft);max-width:62ch}
.four{display:grid;grid-template-columns:1fr 1fr;gap:20px 28px}
.four p{margin:0 0 6px;font-size:15px;color:var(--soft)}.four p b{font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;font-size:26px;color:#fff;margin-right:4px}
.four .plot{min-height:150px}
/* every number a coach reads */
.nh{font-size:28px;margin:44px 0 0}.nh small{font-size:17px;color:var(--muted);letter-spacing:.5px}
.nums{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));margin:16px 0 0;background:var(--ink-2);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.num1{box-shadow:0 0 0 .5px #38322c;padding:14px 14px 12px;min-width:0;display:flex;flex-direction:column}
.num1 .a{margin:0;font-size:14px;line-height:1.3;color:var(--muted)}
.num1 .v{margin:6px 0 0;font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;font-size:30px;line-height:1;font-variant-numeric:tabular-nums}
.num1 .v small{font-family:-apple-system,BlinkMacSystemFont,"Inter","Segoe UI",Helvetica,Arial,sans-serif;font-weight:500;font-size:14px;color:var(--muted);margin-left:4px}
.num1 svg{display:block;width:100%;height:30px;margin:8px 0 0}
.num1 .w{margin:auto 0 0;padding-top:8px;font-size:14px;color:#8a837c}
.nums.short .num1:nth-child(n+13){display:none}
.allnums{margin:16px 0 0;min-height:48px;padding:0 22px;border:1.5px solid var(--orange);border-radius:10px;background:none;color:var(--orange);font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;text-transform:uppercase;letter-spacing:1px;font-size:18px;cursor:pointer}
.allnums:hover{background:var(--orange);color:#12100e}
@media (max-width:860px){.counts,.nums{grid-template-columns:repeat(2,minmax(0,1fr))}.path{grid-template-columns:1fr 1fr}}
@media (max-width:640px){.feed{padding:56px 0}.path,.four{grid-template-columns:1fr}.counts b{font-size:30px}.nh small{display:block;margin-top:4px}.counts div{padding:16px 14px}.nums.short .num1:nth-child(n+9){display:none}.num1{padding:12px}.num1 .v{font-size:26px}}
.cta{padding:88px 0}
@media (max-width:860px){.vizgrid{grid-template-columns:1fr}.lifts{grid-template-columns:1fr}}
@media (max-width:640px){.ch{grid-template-columns:88px 1fr;gap:16px}.ch img{grid-row:auto;width:88px;height:110px}.ch .does,.ch .tags{grid-column:1/-1}.cs{padding:56px 0}.ask{padding:16px}.ask a{width:100%;justify-content:center}.jumpbar .wrap{padding-right:0}.viz{padding:18px 16px 14px}.viz .take{font-size:26px}.intro .lead{font-size:18px}}
</style>"""


def portrait(k, alt, w, h, sizes):
    """Coach portrait as WebP (216 and 432 px wide) with the original JPEG as the fallback."""
    return (f'<picture><source type="image/webp" srcset="/assets/{k}-216.webp 216w, /assets/{k}-432.webp 432w" sizes="{sizes}">'
            f'<img src="/assets/{k}.jpg" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async"></picture>')


def avatar(k, px):
    """Small round coach picture (a 96 px WebP covers 44 px at 2x)."""
    return (f'<picture><source type="image/webp" srcset="/assets/{k}-96.webp">'
            f'<img src="/assets/{k}.jpg" alt="" width="{px}" height="{px}" loading="lazy" decoding="async"></picture>')


FOUR = '<div class="four">' + "".join(f'<div><p id="h-form-{k}">&nbsp;</p><div class="plot" id="p-form-{k}" role="img"></div></div>'
                                      for k in ("gct", "cadence", "step", "vr")) + "</div>"


def spark(v):
    """A number's last values as a small line. No axis: the value and its name are beside it."""
    if len(v) < 4:
        return ""
    lo, hi = min(v), max(v)
    pts = " ".join(f"{i / (len(v) - 1) * 100:.1f},{27 - (x - lo) / ((hi - lo) or 1) * 24:.1f}" for i, x in enumerate(v))
    return (f'<svg viewBox="0 0 100 30" preserveAspectRatio="none" aria-hidden="true"><polyline points="{pts}" fill="none" '
            f'stroke="#ff6a1f" stroke-width="1.6" vector-effect="non-scaling-stroke" stroke-linejoin="round"/></svg>')


MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def md(d):
    return f"{MON[int(d[5:7]) - 1]} {int(d[8:])}"


def fresh(d, now):
    """No date on a number from the last two days; an older one carries its date."""
    import datetime as dt
    return (dt.date.fromisoformat(now) - dt.date.fromisoformat(d)).days <= 2


def numbers(c, feed):
    rows = (feed.get("signals") or {}).get(c["k"]) or []
    if not rows:
        return ""
    cells = "".join(f'<div class="num1"><p class="a">{s["n"]}</p><p class="v">{s["v"]}{"<small>" + s["u"] + "</small>" if s["u"] else ""}</p>'
                    f'{spark(s["s"])}<p class="w">{s["e"]}{"" if fresh(s["d"], feed["updated"]) else " · " + md(s["d"])}</p></div>' for s in rows)
    more = (f'<button class="allnums" type="button" hidden aria-expanded="false" data-more="Show all {len(rows)}" data-less="Show fewer">'
            f'Show all {len(rows)}</button>') if len(rows) > 12 else ""
    return (f'\n    <div><h3 class="nh">Every number {c["n"]} reads <small>{len(rows)}, as of {md(feed["updated"])}</small></h3>'
            f'<div class="nums">{cells}</div>{more}</div>')


def ms(s):
    return f"{int(s) // 60}:{int(s) % 60:02d}"


def data_section(feed):
    """The first section: what goes in, drawn. Tyler tells it (O7); it says what the numbers can't do (W3)."""
    if not feed:
        return ""
    t, r = feed["totals"], feed.get("run") or {}
    since = f'{md(t["since"])}, {t["since"][:4]}'
    big = f'{t["readings"] / 1e6:.1f} million' if t["readings"] >= 1e6 else f'{t["readings"]:,}'
    tiles = [(f'{t["readings"]:,}', "readings off the watch and chest strap"), (f'{t["hours"]:,}', "hours of running, written down every second"),
             (f'{t["runs"]:,}', "runs"), (f'{t["laps"]:,}', "laps"), (f'{t["climb_ft"]:,}', "feet climbed"),
             (f'{t["nights"]:,}', "nights of sleep"), (f'{t["hrv"]:,}', "heart-rhythm readings while I slept"),
             (f'{feed["signals_total"]}', "different numbers the coaches read, all below")]
    counts = "".join(f"<div><b>{v}</b><span>{lab}</span></div>" for v, lab in tiles)
    when = f'{"Mon Tue Wed Thu Fri Sat Sun".split()[__import__("datetime").date.fromisoformat(r["date"]).weekday()]} {md(r["date"])}' if r else ""
    steps = []
    if r:
        steps.append(("I stop the watch.", f'{when}: {r["secs"]:,} seconds and {r["readings"]:,} readings.'))
        if r.get("in_min"):
            steps.append((f'{r["in_min"]} minute{"s" if r["in_min"] != 1 else ""} later it\'s in.', "The file lands on its own. I don't type anything."))
        cl = ""
        if r.get("climbs"):
            cl = f' {r["climbs"]} climb{"s" if r["climbs"] != 1 else ""}' + (f', {r["known"]} of them I\'d run before.' if r.get("known") else ".")
        steps.append(("Kai cuts it up.", f'{r["laps"]} laps.{cl}'))
        if r.get("cap"):
            steps.append(("He checks my heart rate.", f'An easy day stays under {r["cap"]} beats a minute. I was over it for {r["over"]} seconds.' if r.get("over") else f'An easy day stays under {r["cap"]} beats a minute. I never went over.'))
        if r.get("over") and r.get("cap") == 120:
            steps.append(("Kai's call.", "When his heart rate reads one-twenty on that climb, he walks."))
        steps.append(("It's on my watch.", "The next run is there before breakfast. I still have to run it."))
    path = "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in steps)
    every = round(r["span"] / len(r["channels"][0]["v"])) if r else 0
    capline = f' On the heart-rate line, the dashes mark {r["cap"]} beats a minute, the most Kai wants on an easy day. Red is over it.' if r.get("cap") else ""
    reps = f' The {len(r["reps"])} pale stripes are the short hard efforts.' if r.get("reps") else ""
    return f"""
<section class="feed" id="data">
  <div class="wrap">
    <p class="kicker">The data</p>
    <h2 class="display">{big} <span class="o">readings.</span></h2>
    <p class="body">The coaches are drawn. The numbers came off me: a watch, a chest strap and a scale, since {since}. When two coaches argue in the show, this is what they're arguing over. None of it can tell them when something hurts. I have to say that myself.</p>
    <div class="counts">{counts}</div>

    <h3>One run, the way Kai sees it</h3>
    <p>Drag across it. Every line is a different sensor at the same second.</p>
    <figure class="viz" id="v-run"><figcaption><p class="q">What does one run look like to a coach?</p><p class="take" data-take="run">&nbsp;</p></figcaption>
      <div class="plot" id="p-run" role="img" style="min-height:640px"></div>
      <input class="scrub" id="run-at" type="range" min="0" max="319" value="70" aria-label="Move through the run">
      <p class="src">The watch writes a row every second. This draws one point for every {every} seconds so it fits on a screen.{capline}{reps}</p></figure>
    <div class="vizgrid">
      <figure class="viz wide" id="v-beats"><figcaption><p class="q">How fine does it get?</p><p class="take" data-take="beats">&nbsp;</p></figcaption>
        <div class="plot" id="p-beats" role="img"></div>
        <p class="src">One minute from the middle of that run, one dot a heartbeat. The chest strap times the gap between beats to a thousandth of a second, and the higher dots are the longer gaps. It started saving every beat on {md(feed["beats"]["date"]) if feed.get("beats") else ""}.</p></figure>
      <figure class="viz wide" id="v-all"><figcaption><p class="q">How far back can they look?</p><p class="take" data-take="all">&nbsp;</p>
        <p class="key"><span><i class="sw muted"></i>Lower heart rate</span><span><i class="sw orange"></i>Higher heart rate</span></p></figcaption>
        <div class="plot" id="p-all" role="img" style="min-height:280px"></div><p class="tip" id="tip-all" aria-live="polite"></p>
        <p class="src">Pace per mile, faster at the top. Bigger dots are longer runs. The 1:32:31 half is up there in June 2024. This fall is on the right. Anything slower than 16:00 sits on the bottom edge. Runs under half a mile, and the few the watch lost its place on, aren't drawn.</p></figure>
    </div>

    <h3>What happens to a run</h3>
    <p>This is the last one, step by step.</p>
    <ol class="path">{path}</ol>
    <p class="fine" style="margin-top:28px">Left off on purpose: where I run, the number on the scale, and anything about my kids.</p>
  </div>
</section>"""


def section(c, co, feed):
    k, x = c["k"], co[c["n"]]
    tags = "".join(f"<span>{t}</span>" for t in c["watch"])
    charts = c["charts"]
    figs = ""
    for i, (cid, q, src, *key) in enumerate(charts):
        wide = " wide" if (len(charts) % 2 == 1 and i == len(charts) - 1 and len(charts) > 1) else ""
        keys = "".join(f'<span><i class="sw {sw}"></i>{lab}</span>' for sw, lab in (key[0] if key else []))
        keys = f'<p class="key">{keys}</p>' if keys else ""
        figs += (f'\n      <figure class="viz{wide}" id="v-{cid}">'
                 f'<figcaption><p class="q">{q}</p><p class="take" data-take="{cid}">&nbsp;</p>{keys}</figcaption>'
                 + (FOUR if cid == "form" else f'<div class="plot" id="p-{cid}" role="img"></div>') + f'<p class="src">{src}</p></figure>')
    if k == "bo":
        figs += '\n      <div class="lifts" id="p-lifts"></div>'
    one = " one" if len(charts) <= 1 else ""
    return f"""
<section class="cs" id="{k}">
  <div class="wrap">
    <div class="ch">
      {portrait(k, f"{c['n']}, the {c['role']}", 400, 500, "(max-width:640px) 88px, 148px")}
      <div>
        <p class="kicker">{c['role']}</p>
        <h2 class="display">{c['n']}</h2>
      </div>
      <p class="does">{c['does']}</p>
      <div class="tags" aria-label="What {c['n']} watches">{tags}</div>
    </div>
    <blockquote class="say">{avatar(k, 44)}<p data-line="{c['line']}"></p></blockquote>
    <div class="vizgrid{one}">{figs}
    </div>{numbers(c, feed)}
  </div>
</section>"""


def main():
    home = (ROOT / "index.html").read_text()
    d = json.loads((ROOT / "data" / "progress.json").read_text())
    co = d["coaches"]
    ff = ROOT / "data" / "feed.json"
    feed = json.loads(ff.read_text()) if ff.exists() else {}
    ver = re.search(r"/assets/ui\.css\?v=(\w+)", home).group(1)
    gtm = home[home.index("<!-- Google tag"):home.index("<title>")]
    style = re.search(r"<style>.*?</style>", home, re.S).group(0).replace("url(assets/", "url(/assets/")
    jump = '<a href="#data" class="jd">The data</a>' + "".join(f'<a href="#{c["k"]}">{avatar(c["k"], 28)}{c["n"]}</a>' for c in COACHES)
    desc = "Meet the five AI coaches in To The Finish. See my real running, strength, recovery and food data, and what each coach does with it."
    schema = json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": "The coaches | To The Finish",
                         "url": "https://tothefinish.ai/coaches/", "description": desc,
                         "isPartOf": {"@type": "WebSite", "name": "To The Finish", "url": "https://tothefinish.ai/"}},
                        ensure_ascii=False)
    body = "".join(section(c, co, feed) for c in COACHES)
    counts = " · ".join(f'{c["n"]} <b data-k="c_{c["k"]}_studies">{co[c["n"]]["studies"]}</b> studies and '
                        f'<b data-k="c_{c["k"]}_live">{co[c["n"]]["live"]:,}</b> {c["live"]}' for c in COACHES)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{gtm}<title>The coaches · To The Finish</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="The coaches · To The Finish">
<meta property="og:description" content="{desc}">
<meta property="og:site_name" content="To The Finish">
<meta property="og:image:alt" content="Tyler and the five animated To The Finish coaches">
<meta name="robots" content="index,follow,max-image-preview:large,max-video-preview:-1">
<meta property="og:image" content="https://tothefinish.ai/assets/og.jpg">
<meta property="og:url" content="https://tothefinish.ai/coaches/">
<meta property="og:type" content="website">
<link rel="canonical" href="https://tothefinish.ai/coaches/">
<script type="application/ld+json">{schema}</script>
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="The coaches · To The Finish">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://tothefinish.ai/assets/og.jpg">
<link rel="preload" as="font" type="font/woff2" href="/assets/barlow-condensed-800.woff2" crossorigin>
<link rel="icon" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
{style}
{CSS}
<link rel="stylesheet" href="/assets/ui.css?v={ver}">
<link rel="stylesheet" href="/assets/motion.css?v={ver}">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<main id="main">

<header class="top" style="padding-bottom:0">
  <div class="wrap">
    <div class="bar">
      <a class="mark" href="/">TO THE <span class="o">FINISH.</span></a>
      {site_nav("/coaches/")}
    </div>
  </div>
</header>

<div class="intro"><div class="wrap">
  <p class="kicker">The coaches</p>
  <h1 class="display">What they <span class="o">see.</span></h1>
  <p class="lead">Five cartoon coaches, reading real numbers off a real body. Here's everything that goes in, what each coach said about this week, and the one thing each of them can't do.</p>
</div></div>
<div class="jumpbar"><div class="wrap"><nav class="jump" aria-label="Coaches">{jump}</nav></div></div>
{data_section(feed)}
{body}

<section class="cta">
  <div class="wrap">
    <p class="kicker">Come along</p>
    <h2 class="display">Follow the <span class="o">chase.</span></h2>
    <p class="body" style="text-wrap:pretty">Sunday nights I write down what the week really was, and the calls each coach made about it.</p>
    <p style="margin-top:24px"><a class="btn" style="background:var(--orange)" href="/#letter">Get the Sunday letter</a></p>
    <p class="fine">One email a week. Leave any time.</p>
    <p class="fine">Behind the rules: <b data-k="c_all">{co['all_studies']}</b> studies in all. {counts}. One study can sit behind more than one coach.</p>
  </div>
</section>

</main>
{site_footer()}

<script src="/assets/charts.js?v={ver}"></script>
<script src="/assets/coaches-page.js?v={ver}"></script>
<script src="/assets/feed.js?v={ver}"></script>
<script src="/assets/motion.js?v={ver}" defer></script>
</body>
</html>
"""
    out = ROOT / "coaches"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(page)
    print(f"built coaches ({len(page) // 1024} KB)")


if __name__ == "__main__":
    main()
