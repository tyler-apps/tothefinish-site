#!/usr/bin/env python3
"""Build /coaches/: what each AI coach watches, what they do with it, and the numbers they're watching now.

Tyler 2026-11-21: "redesign the charts for a coaches page". The homepage stays short; this page carries the charts,
drawn by assets/charts.js (one chart system) from data/progress.json via assets/coaches-page.js. Header, footer
and type come from the homepage so both pages read as one site. Re-run by tools/publish.sh.

2026-11-21, Sanderson full read (people before systems): each coach now opens with their own line on this week's
numbers, then what they do and the one thing they can't, then the charts. The study and work counts sit in one line at
the foot. One waitlist ask on the page, at the end; the per-coach interest links moved there (GA4 coach_interest).
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
                  [("muted", "Ran"), ("ghost", "Planned"), ("orange", "This week")])],
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
                  [("orange", "7 hours or more"), ("muted", "Under 7"), ("dim", "Broken night")])],
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
               "or the fridge updates what's there. Portions come from my 7-day weigh-in trend, so I lose no more "
               "than 2 lb a week. She can't change a food rule without my word."),
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
                  "Garmin's marathon prediction after every run since October 19, against what Chicago asks for."),
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
.key{display:flex;flex-wrap:wrap;gap:6px 16px;margin:-6px 0 14px;font-size:13px;color:var(--soft)}
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


def section(c, co):
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
                 f'<div class="plot" id="p-{cid}" role="img"></div><p class="src">{src}</p></figure>')
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
    </div>
  </div>
</section>"""


def main():
    home = (ROOT / "index.html").read_text()
    d = json.loads((ROOT / "data" / "progress.json").read_text())
    co = d["coaches"]
    ver = re.search(r"/assets/ui\.css\?v=(\w+)", home).group(1)
    gtm = home[home.index("<!-- Google tag"):home.index("<title>")]
    style = re.search(r"<style>.*?</style>", home, re.S).group(0).replace("url(assets/", "url(/assets/")
    jump = "".join(f'<a href="#{c["k"]}">{avatar(c["k"], 28)}{c["n"]}</a>' for c in COACHES)
    desc = ("What each of my five AI coaches watches, what they do with it, and the numbers they're watching right now: "
            "running, recovery, strength, fuel and the calls between them.")
    schema = json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": "The coaches | To The Finish",
                         "url": "https://tothefinish.ai/coaches/", "description": desc,
                         "isPartOf": {"@type": "WebSite", "name": "To The Finish", "url": "https://tothefinish.ai/"}},
                        ensure_ascii=False)
    body = "".join(section(c, co) for c in COACHES)
    pick = " · ".join(f'<a href="/?coach={c["k"]}#waitlist" data-coach="{c["k"]}">{c["n"]}</a>' for c in COACHES)
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
<meta property="og:description" content="Five AI coaches read my runs, sleep, lifts and meals as they happen, and change my plan on their own. Here's what each one is watching right now.">
<meta property="og:image" content="https://tothefinish.ai/assets/og.jpg">
<meta property="og:url" content="https://tothefinish.ai/coaches/">
<meta property="og:type" content="website">
<link rel="canonical" href="https://tothefinish.ai/coaches/">
<script type="application/ld+json">{schema}</script>
<meta name="twitter:card" content="summary_large_image">
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
  <p class="lead">Five AI coaches read every run, night of sleep and weigh-in, and each one makes a call. Here's what each coach said about this week's numbers, the one thing they can't do, and the charts they're reading.</p>
</div></div>
<div class="jumpbar"><div class="wrap"><nav class="jump" aria-label="Coaches">{jump}</nav></div></div>
{body}

<section class="cta">
  <div class="wrap">
    <p class="kicker">Come along</p>
    <h2 class="display">Want your own <span class="o">AI coaching team?</span></h2>
    <p class="body" style="text-wrap:pretty">Right now it coaches one guy. When it's ready for a second runner, the waitlist hears first.</p>
    <p style="margin-top:24px"><a class="btn" style="background:var(--orange)" href="/#waitlist">Get on the waitlist</a></p>
    <p class="fine">The waitlist comes with my Sunday letter. One email a week. Leave any time.</p>
    <p class="fine">Which coach would you want first? {pick}</p>
    <p class="fine">Behind the rules: <b data-k="c_all">{co['all_studies']}</b> studies in all. {counts}. One study can sit behind more than one coach.</p>
  </div>
</section>

{site_footer()}

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
