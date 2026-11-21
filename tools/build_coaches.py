#!/usr/bin/env python3
"""Build /coaches/: what each AI coach watches, what they do with it, and the numbers they're watching now.

Tyler 2026-11-21: "redesign the charts for a coaches page". The homepage stays short; this page carries the charts,
drawn by assets/charts.js (one chart system) from data/progress.json via assets/coaches-page.js. Header, footer
and type come from the homepage so both pages read as one site. Re-run by tools/publish.sh.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COACHES = [
    dict(k="kai", n="Kai", role="AI running coach", live="runs read",
         watch=["Every lap and split", "Heart rate from a chest strap", "Hills and grade", "Heat and weather",
                "Threshold pace", "Race results"],
         does=("Builds the year race by race, a 5K, a 10K, a half, then the marathon, and sets every pace and "
               "heart-rate zone from my own runs. A slow mile up a climb gets credit for the faster flat mile it "
               "took the same effort to run."),
         charts=[("engine", "Is the engine coming back?",
                  "Lactate-threshold pace from my Garmin: about the fastest I can hold for an hour. Higher is faster."),
                 ("eff", "Am I fitter at the same heart rate?",
                  "Meters I travel for each heartbeat on easy runs, four-week average, hills evened out. Higher is fitter."),
                 ("miles", "Am I running the miles?",
                  "Planned miles each week to Chicago (outlines) and the miles I ran (filled).")],
         line="kai_year"),
    dict(k="mo", n="Mo", role="AI recovery coach", live="nights of sleep read",
         watch=["Hours asleep", "Resting heart rate", "Heart rate variability", "Every run's length",
                "Easy-day heart rate", "My legs and pain check-ins"],
         does=("Reads my sleep and resting heart rate, and they can only ever make a day easier. Checks every run "
               "against the longest of the month, where overuse injuries start, and builds the warm-ups, prehab and "
               "down weeks around the plan."),
         charts=[("easy", "Are the easy days easy?",
                  "Share of each week's running time at easy heart rate, my zone 2 or below. The best distance "
                  "runners keep at least 80% easy."),
                 ("sleep", "Am I sleeping enough?",
                  "Hours asleep each night from my watch. Faded bars were broken nights, which watches count long.")],
         line="mo_sleep"),
    dict(k="bo", n="Bo", role="AI strength coach", live="lifts tracked",
         watch=["The top set I text after each lift", "The run calendar", "Which days carry a hard run"],
         does=("Heavy sets of three and jumps, the strength work that makes runners faster, fitted around the run "
               "and never the other way around. Sets my next weights from my last top sets."),
         charts=[], line="bo"),
    dict(k="juno", n="Juno", role="AI nutritionist", live="foods measured",
         watch=["Today's and tomorrow's run", "The food in the house", "Grocery receipts and fridge photos",
                "The meals on the plan", "My 7-day weigh-in trend"],
         does=("Writes my food every day from the run it has to fuel and what's in the house. A photo of a receipt "
               "or the fridge updates what's there. Portions come from my 7-day weigh-in trend, so I lose no more "
               "than 2 lb a week."),
         charts=[("fuel", "Does the food follow the work?",
                  "Grams of carbs a day from my meal plan, the next seven days. Orange days carry a hard or long run.")],
         line="juno"),
    dict(k="rook", n="Rook", role="AI head coach", live="decisions made",
         watch=["Every coach's plan", "The priority board", "Every call the coaches make", "What I tell the coaches"],
         does=("Settles every clash between the coaches: what I say and any pain first, then Chicago, then weight, "
               "then strength. Tracks the gap to sub-3 every morning and writes down every decision the team makes."),
         charts=[("gap", "Am I closing the gap?",
                  "Garmin's marathon prediction after every run since October 19, against what Chicago asks for."),
                 ("calls", "Who makes the calls?",
                  "Every decision the coaches wrote down since Nov 9. Orange were made automatically from my watch "
                  "data, white are a coach's own call, gray the times I overruled one.")],
         line="rook"),
]

CSS = """<style>
.intro{padding:24px 0 56px}
.intro h1{font-size:clamp(52px,8vw,104px)}
.intro .lead{font-size:20px;line-height:1.5;color:var(--soft);max-width:44ch;margin:20px 0 0}
.jump{display:flex;flex-wrap:wrap;gap:8px;margin-top:28px}
.jump a{display:inline-flex;align-items:center;gap:8px;padding:6px 14px 6px 6px;border:1px solid var(--line);border-radius:999px;text-decoration:none;font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;text-transform:uppercase;letter-spacing:1px;font-size:17px;background:var(--ink-2)}
.jump a:hover{border-color:var(--orange)}
.jump img{width:28px;height:28px;border-radius:50%;object-fit:cover}
.cs{padding:88px 0}
.ch{display:grid;grid-template-columns:148px 1fr;gap:0 28px;align-items:start}
.ch img{grid-row:1/span 3;width:148px;height:185px;object-fit:cover;object-position:50% 20%;border-radius:14px;border:1px solid var(--line)}
.ch h2{font-size:clamp(48px,6vw,72px)}
.ch .kicker{margin-bottom:8px}
.ch .proof{margin:12px 0 0;font-size:15px;color:var(--muted)}
.ch .proof b{color:var(--orange);font-weight:700}
.ch .does{margin:14px 0 0;font-size:18px;line-height:1.55;color:var(--soft);max-width:62ch}
.ch .does,.ch .tags{grid-column:2}
.tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.tags span{padding:5px 11px;border-radius:999px;border:1px solid #4a433c;font-size:13px;color:#e7e2dc}
.vizgrid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:40px}
.vizgrid.one{grid-template-columns:1fr}
.viz{margin:0;background:var(--ink-2);border:1px solid var(--line);border-radius:16px;padding:22px 22px 18px;min-width:0}
.viz.wide{grid-column:1/-1}
.viz .q{margin:0;font-size:14px;font-weight:600;color:var(--muted)}
.viz .take{margin:6px 0 18px;font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;text-transform:uppercase;font-size:30px;line-height:1.05}
.viz .take b{color:var(--orange);font-weight:800}
.viz .take span{color:var(--muted)}
.plot{width:100%;min-height:200px}
.src{margin:14px 0 0;font-size:13px;line-height:1.5;color:var(--muted)}
.lifts{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.lift{background:var(--ink-2);border:1px solid var(--line);border-radius:16px;padding:22px}
.lift .n{font-size:14px;font-weight:600;color:var(--muted);margin:0}
.lift .v{font-family:"Barlow Condensed",Impact,sans-serif;font-weight:800;font-size:56px;line-height:1;margin:8px 0 0}
.lift .v small{font-size:.4em;color:var(--muted);margin-left:4px}
.lift .s{font-size:14px;color:var(--soft);margin:10px 0 0}
.say{display:flex;gap:14px;align-items:flex-start;margin:20px 0 0;padding:16px 18px;background:var(--ink-2);border-left:4px solid var(--orange);border-radius:10px;max-width:820px}
.say img{width:44px;height:44px;border-radius:50%;object-fit:cover;flex:none}
.say p{margin:0;font-size:17px;line-height:1.5}
.cta{padding:88px 0}
@media (max-width:860px){.vizgrid{grid-template-columns:1fr}.lifts{grid-template-columns:1fr}}
@media (max-width:640px){.ch{grid-template-columns:88px 1fr;gap:16px}.ch img{grid-row:auto;width:88px;height:110px}.ch .does,.ch .tags{grid-column:1/-1}.cs{padding:64px 0}.viz{padding:18px 16px 14px}.viz .take{font-size:26px}.intro .lead{font-size:18px}}
</style>"""


def section(c, co):
    k, x = c["k"], co[c["n"]]
    tags = "".join(f"<span>{t}</span>" for t in c["watch"])
    charts = c["charts"]
    figs = ""
    for i, (cid, q, src) in enumerate(charts):
        wide = " wide" if (len(charts) % 2 == 1 and i == len(charts) - 1 and len(charts) > 1) else ""
        figs += (f'\n      <figure class="viz{wide}" id="v-{cid}">'
                 f'<figcaption><p class="q">{q}</p><p class="take" data-take="{cid}">&nbsp;</p></figcaption>'
                 f'<div class="plot" id="p-{cid}" role="img"></div><p class="src">{src}</p></figure>')
    if k == "bo":
        figs += '\n      <div class="lifts" id="p-lifts"></div>'
    one = " one" if len(charts) <= 1 else ""
    return f"""
<section class="cs" id="{k}">
  <div class="wrap">
    <div class="ch">
      <img src="/assets/{k}.jpg" alt="{c['n']}, the {c['role']}" width="400" height="500" loading="lazy">
      <div>
        <p class="kicker">{c['role']}</p>
        <h2 class="display">{c['n']}</h2>
        <p class="proof"><b data-k="c_{k}_studies">{x['studies']}</b> studies read · <b data-k="c_{k}_live">{x['live']:,}</b> {c['live']}</p>
      </div>
      <p class="does">{c['does']}</p>
      <div class="tags" aria-label="What {c['n']} watches">{tags}</div>
    </div>
    <div class="vizgrid{one}">{figs}
    </div>
    <blockquote class="say"><img src="/assets/{k}.jpg" alt="" width="44" height="44"><p data-line="{c['line']}"></p></blockquote>
  </div>
</section>"""


def main():
    home = (ROOT / "index.html").read_text()
    d = json.loads((ROOT / "data" / "progress.json").read_text())
    co = d["coaches"]
    ver = re.search(r"/assets/ui\.css\?v=(\w+)", home).group(1)
    gtm = home[home.index("<!-- Google tag"):home.index("<title>")]
    style = re.search(r"<style>.*?</style>", home, re.S).group(0).replace("url(assets/", "url(/assets/")
    links = re.search(r'<div class="links">.*?</div>', home, re.S).group(0)
    nav = ('<nav class="nav" aria-label="Main"><a href="/#why">Why</a><a href="/coaches/" aria-current="page">The coaches</a>'
           '<a href="/episodes/">Episodes</a><a href="/san-diego-races/">San Diego races</a><a href="/chicago-marathon-2027/">Chicago</a>'
           '<a class="navcta" href="/#club">Join</a></nav>')
    mnav = ('<details class="mnav"><summary aria-label="Menu">Menu</summary><nav aria-label="Main"><a href="/#why">Why</a>'
            '<a href="/coaches/">The coaches</a><a href="/episodes/">Episodes</a><a href="/san-diego-races/">San Diego races</a>'
            '<a href="/chicago-marathon-2027/">Chicago</a><a href="/#club">Join</a></nav></details>')
    jump = "".join(f'<a href="#{c["k"]}"><img src="/assets/{c["k"]}.jpg" alt="">{c["n"]}</a>' for c in COACHES)
    body = "".join(section(c, co) for c in COACHES)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{gtm}<title>The coaches · To The Finish</title>
<meta name="description" content="What each of my five AI coaches watches, what they do with it, and the numbers they're watching right now: running, recovery, strength, fuel and the calls between them.">
<meta property="og:title" content="The coaches · To The Finish">
<meta property="og:description" content="Five AI coaches read my runs, sleep, lifts and meals as they happen, and change my plan on their own. Here's what each one is watching right now.">
<meta property="og:image" content="https://tothefinish.ai/assets/og.jpg">
<meta property="og:url" content="https://tothefinish.ai/coaches/">
<link rel="canonical" href="https://tothefinish.ai/coaches/">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
{style}
{CSS}
<link rel="stylesheet" href="/assets/ui.css?v={ver}">
<link rel="stylesheet" href="/assets/motion.css?v={ver}">
</head>
<body>

<header class="top" style="padding-bottom:0">
  <div class="wrap">
    <div class="bar">
      <a class="mark" href="/">TO THE <span class="o">FINISH.</span></a>
      {nav}
      {mnav}
    </div>
  </div>
</header>

<div class="intro"><div class="wrap">
  <p class="kicker">The coaches</p>
  <h1 class="display">What they <span class="o">see.</span></h1>
  <p class="lead">Every run, night of sleep and weigh-in reaches five AI coaches on its own, and they change my plan on their own. Between them they've read <b data-k="c_all">{co['all_studies']}</b> studies. Here's what each one watches, and the numbers they're watching right now.</p>
  <nav class="jump" aria-label="Coaches">{jump}</nav>
</div></div>
{body}

<section class="cta">
  <div class="wrap">
    <p class="kicker">Come along</p>
    <h2 class="display">Want your own <span class="o">AI coaching team?</span></h2>
    <p class="body">Right now it coaches one guy. If it gets me to Chicago, you'll get to try it first.</p>
    <p style="margin-top:24px"><a class="btn" style="background:var(--orange)" href="/#club">Get on the list</a></p>
  </div>
</section>

<footer>
  <div class="wrap">
    <p class="sign">Not built for it. <span class="o">Training for it anyway.</span></p>
    {links}
    <p>Contact: <a href="mailto:hello@tothefinish.ai">hello@tothefinish.ai</a></p>
    <p>My personal AI coaching setup. Not medical or nutrition advice. The coaches are AI characters.</p>
  </div>
</footer>

<script src="/assets/charts.js?v={ver}"></script>
<script src="/assets/coaches-page.js?v={ver}"></script>
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
