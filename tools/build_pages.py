#!/usr/bin/env python3
"""build_pages.py: builds the SEO pages for tothefinish.ai from episodes/episodes.json.

Tyler 2026-11-18: "Should we go for an SEO play on the website" -> "Build". The plan
(Brain: brain/methods/social/growth-playbook.md + brain/social/automation.md): one page per
episode (the video, a short write-up in Tyler's voice, one search phrase, the sign-up form,
VideoObject structured data), an episodes index, the "AI running coach" page, sitemap.xml and
robots.txt. The home page stays hand-edited; this script never touches index.html.

    python3 tools/build_pages.py          # rebuild everything from episodes/episodes.json

episodes.json is a list, newest last, of:
  {"number": 1, "slug": "the-hiring", "title": "The Hiring", "date": "2026-11-22",
   "youtube_id": "XXXXXXXXXXX", "vertical": false, "duration": "PT4M10S",
   "phrase": "sub-3 marathon at 258 lb", "description": "one or two sentences (meta + list)",
   "writeup": ["paragraph", "paragraph"], "garmin": "one true line from the week's data (optional)"}
Only published episodes go in the file. Every word follows the To The Finish voice rules
(first person, true facts only, no AI tells); the generator adds nothing of its own beyond labels.
"""
import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://tothefinish.ai"
GTM = "GTM-5Q6Q2KFL"
TODAY = dt.date.today().isoformat()


def esc(s):
    return html.escape(s or "", quote=True)


def head(title, desc, path, extra=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script async src="https://www.googletagmanager.com/gtm.js?id={GTM}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());</script>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/assets/og.jpg">
<meta property="og:url" content="{SITE}{path}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/site.css">
{extra}
</head>
<body>
<header class="page-top">
  <div class="wrap">
    <div class="bar">
      <a class="mark" href="/">TO THE <span class="o">FINISH.</span></a>
      <nav class="nav"><a href="/#progress">Progress</a><a href="/episodes/">Episodes</a><a href="/ai-running-coach/">The coaches</a><a href="/#club">Train with us</a></nav>
    </div>
"""


FORM = """<form class="join" id="join-{id}" data-thanks="thanks-{id}">
  <input name="fields[first_name]" placeholder="First name" autocomplete="given-name">
  <input name="email_address" type="email" placeholder="Email" required autocomplete="email">
  <button type="submit">{button}</button>
</form>
<div class="thanks" id="thanks-{id}">You're in. The first email comes Sunday with the week's miles and the new episode.</div>
<p class="fine">One email every Sunday: my week's miles and the new episode.</p>"""

FOOT = """<footer>
  <div class="wrap">
    <p class="sign">Not built for it. <span class="o">Training for it anyway.</span></p>
    <div class="links"><a href="https://www.youtube.com/@tothefinishai">YouTube</a><a href="https://www.instagram.com/tothefinishai/">Instagram</a><a href="https://www.tiktok.com/@tothefinishai">TikTok</a><a href="https://x.com/tothefinishai">X</a><a href="https://www.strava.com/clubs/tothefinish">Strava</a></div>
    <p>Contact: <a href="mailto:hello@tothefinish.ai">hello@tothefinish.ai</a></p>
    <p>My personal AI coaching setup. Not medical or nutrition advice. The coaches are AI characters.</p>
  </div>
</footer>
<iframe name="hidden_iframe" id="hidden_iframe" style="display:none" title="form target"></iframe>
<script src="/assets/join.js"></script>
</body>
</html>
"""


ROBOTS = """# tothefinish.ai robots.txt (reviewed 2026-11-18; Brain: brain/methods/social/sources/aeo-t1.md)

# Search and answer engines: needed to be cited in AI answers
User-agent: Googlebot
User-agent: Bingbot
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: Applebot
Allow: /

# Model training and Gemini grounding: allowed on purpose
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Google-Extended
User-agent: Applebot-Extended
Allow: /

User-agent: *
Allow: /

Sitemap: {site}/sitemap.xml
"""


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


def episode_page(e):
    path = f"/episodes/{e['slug']}/"
    title = f"Episode {e['number']}: {e['title']} | To The Finish, the AI running coach show"
    thumb = f"https://i.ytimg.com/vi/{e['youtube_id']}/maxresdefault.jpg"
    video = {
        "@context": "https://schema.org", "@type": "VideoObject",
        "name": f"To The Finish, Episode {e['number']}: {e['title']}",
        "description": e["description"], "thumbnailUrl": [thumb],
        "uploadDate": e["date"], "embedUrl": f"https://www.youtube.com/embed/{e['youtube_id']}",
        "partOfSeries": {"@type": "CreativeWorkSeries", "name": "To The Finish", "alternateName": "To The Finish AI running coach", "url": SITE + "/"},
    }
    if e.get("duration"):
        video["duration"] = e["duration"]
    body = "".join(f"<p>{esc(p)}</p>" for p in e.get("writeup", []))
    garmin = f'<p class="note">From my Garmin: {esc(e["garmin"])}</p>' if e.get("garmin") else ""
    vclass = "video vertical" if e.get("vertical") else "video"
    date_h = dt.date.fromisoformat(e["date"]).strftime("%B %-d, %Y")
    return head(title, e["description"], path, ld(video)) + f"""    <div class="page">
      <p class="kicker">Episode {e['number']} · {date_h}</p>
      <h1 class="display">{esc(e['title'])}</h1>
    </div>
  </div>
</header>
<section>
  <div class="wrap">
    <div class="{vclass}"><iframe src="https://www.youtube-nocookie.com/embed/{esc(e['youtube_id'])}" title="{esc(e['title'])}" loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>
    <div class="prose" style="margin-top:28px">{body}{garmin}</div>
  </div>
</section>
<section>
  <div class="wrap">
    <p class="kicker">Follow along</p>
    <h2 class="display" style="font-size:clamp(40px,6vw,64px);margin-bottom:18px">The next episode, <span class="o">every Sunday.</span></h2>
    {FORM.format(id='ep', button='Follow along')}
    <p class="body" style="margin-top:22px"><a href="/episodes/">All episodes</a></p>
  </div>
</section>
""" + FOOT


def episodes_index(eps):
    path = "/episodes/"
    desc = ("Every episode of To The Finish, the AI running coach show: a 258 lb dad of two training for a sub-3 marathon at Chicago, "
            "coached by four AI coaches, with the real numbers from his Garmin.")
    if eps:
        items = "".join(
            f'<li><a href="/episodes/{e["slug"]}/"><span class="n">Episode {e["number"]} · '
            f'{dt.date.fromisoformat(e["date"]).strftime("%b %-d, %Y")}</span><h3>{esc(e["title"])}</h3>'
            f'<p>{esc(e["description"])}</p></a></li>' for e in reversed(eps))
        listing = f'<ul class="eplist">{items}</ul>'
    else:
        listing = '<p class="body">Episode 1 comes out Sunday, November 22. Sign up and it lands in your inbox.</p>'
    series = {"@context": "https://schema.org", "@type": "CreativeWorkSeries", "name": "To The Finish",
              "url": SITE + "/", "description": desc}
    return head("Episodes | To The Finish, the AI running coach show", desc, path, ld(series)) + f"""    <div class="page">
      <p class="kicker">Season 1: The 5K</p>
      <h1 class="display">The <span class="o">episodes.</span></h1>
      <p class="lead">One episode every Sunday, from the first week of training to the start line in Chicago. The numbers in them come off my watch.</p>
    </div>
  </div>
</header>
<section>
  <div class="wrap">
    {listing}
    <div style="margin-top:36px">{FORM.format(id='idx', button='Follow along')}</div>
  </div>
</section>
""" + FOOT


def coach_page(qs=()):
    path = "/ai-running-coach/"
    desc = ("My AI running coach is a team of four: running, strength, nutrition and a head coach who settles "
            "it when they disagree. It reads my Garmin data and plans my week toward a sub-3 marathon.")
    org = {"@context": "https://schema.org", "@type": "WebPage", "name": "AI running coach | To The Finish",
           "url": SITE + path, "description": desc}
    return head("AI Running Coach: four coaches, one sub-3 attempt | To The Finish", desc, path, ld(org)) + """    <div class="page">
      <p class="kicker">The coaches</p>
      <h1 class="display">My AI running <span class="o">coach.</span></h1>
      <p class="lead">My AI running coach isn't one coach. It's four, and they argue. Right now the setup coaches one runner: me, starting at 258 lb, training for a sub-3 marathon at Chicago on October 10, 2027.</p>
    </div>
  </div>
</header>
<section>
  <div class="wrap prose">
    <h2>Who does what</h2>
    <p><b>Kai</b> plans every run from my Garmin data: the easy days, the hill sprints, the long run, and the paces each one should feel like.</p>
    <p><b>Bo</b> fits four short lifts around the running, and he always wants my legs on the wrong day.</p>
    <p><b>Juno</b> plans my meals around the training and makes sure I eat enough to run.</p>
    <p><b>Rook</b> is the head coach. When the other three want different things from the same week, he decides.</p>
    <h2>How it decides</h2>
    <p>Rook settles every clash in the same order: anything I report, like pain, comes first. Then the race in Chicago. Then my weight. Then strength. So when Bo wants heavy legs the day before a hard run, the run usually wins.</p>
    <p>The plan comes from real coaching methods, and every change is written down with the rule behind it. The coaches are AI characters, and this is my personal setup, not medical or nutrition advice.</p>
    <h2>Questions people ask</h2>
    <ul class="qlist">""" + "".join(f'<li><a href="/{q["slug"]}/">{esc(q["question"])}</a></li>' for q in qs) + """</ul>
    <h2>Can I use it?</h2>
    <p>Not yet. It has to get me to Chicago first. If it does, the people on this list get to try it first.</p>
  </div>
</section>
<section>
  <div class="wrap">
    <form class="join" id="join-coach" data-thanks="thanks-coach">
      <input name="fields[first_name]" placeholder="First name" autocomplete="given-name">
      <input name="email_address" type="email" placeholder="Email" required autocomplete="email">
      <input class="wide" name="fields[training_for]" placeholder="What are you training for? (race and date)">
      <button type="submit">Get on the list</button>
    </form>
    <div class="thanks" id="thanks-coach">You're on the list. Reply to the first email with your race. I want to know.</div>
    <p class="body" style="margin-top:22px"><a href="/episodes/">Watch the episodes</a></p>
  </div>
</section>
""" + FOOT


AUTHOR = {"@type": "Person", "name": "Tyler Stewart", "url": SITE + "/ai-running-coach/"}


def question_page(q, all_q):
    path = f"/{q['slug']}/"
    upd = dt.date.fromisoformat(q["updated"]).strftime("%B %-d, %Y")
    art = {"@context": "https://schema.org", "@type": "Article", "headline": q["title"][:110],
           "description": q["description"], "author": AUTHOR,
           "datePublished": q.get("published", q["updated"]) + "T08:00:00-08:00",
           "dateModified": q["updated"] + "T08:00:00-08:00",
           "publisher": {"@type": "Organization", "name": "To The Finish", "url": SITE + "/",
                         "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo.png"}},
           "mainEntityOfPage": SITE + path}
    out = "".join(f"<p>{esc(p)}</p>" for p in q["answer"])
    for sec in q.get("sections", []):
        out += f"<h2>{esc(sec['h2'])}</h2>"
        if sec.get("table"):
            rows = sec["table"]
            th = "".join(f"<th>{esc(c)}</th>" for c in rows[0])
            tb = "".join("<tr>" + "".join(f'<td data-label="{esc(h)}">{esc(c)}</td>' for h, c in zip(rows[0], r)) + "</tr>" for r in rows[1:])
            out += f'<div class="tablewrap"><table class="qt"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>'
        out += "".join(f"<p>{esc(p)}</p>" for p in sec.get("paras", []))
    others = "".join(f'<li><a href="/{o["slug"]}/">{esc(o["question"])}</a></li>' for o in all_q if o["slug"] != q["slug"])
    return head(q["title"] + " | To The Finish AI running coach", q["description"], path, ld(art)) + f"""    <div class="page">
      <p class="kicker">Updated {upd}</p>
      <h1 class="display" style="font-size:clamp(40px,6.5vw,76px)">{esc(q['question'])}</h1>
    </div>
  </div>
</header>
<section>
  <div class="wrap prose">{out}
    <p class="note">By Tyler Stewart. Numbers from my Garmin (chest-strap heart rate). Not medical or nutrition advice; the coaches are AI characters.</p>
  </div>
</section>
<section>
  <div class="wrap">
    <p class="kicker">Follow the test</p>
    {FORM.format(id='q', button='Follow along')}
    <div class="prose" style="margin-top:26px"><h2>More questions</h2><ul class="qlist">{others}<li><a href="/ai-running-coach/">How my AI running coach works</a></li></ul></div>
  </div>
</section>
""" + FOOT



# ---------- live numbers (Tyler 2026-11-18: "Yes, auto-publish numbers") ----------
# Question pages write {placeholders}; values come from data/progress.json (built from Garmin by the Brain's
# scripts/site_progress.py). A page's "Updated" date moves only when one of ITS numbers changes
# (state in pages/.facts-state.json), so a rebuild with nothing new changes nothing.
import hashlib, re

def _sec(p):
    a = [int(x) for x in p.split(":")]
    return a[0] * 3600 + a[1] * 60 + a[2] if len(a) == 3 else a[0] * 60 + a[1]


def facts():
    d = json.loads((ROOT / "data" / "progress.json").read_text())
    D = dt.date.fromisoformat
    long_ = lambda x: D(x).strftime("%B %-d, %Y")
    short = lambda x: D(x).strftime("%b %-d, %Y")
    month = lambda x: D(x).strftime("%b %Y")
    eng = d.get("engine") or []
    best = min(eng, key=lambda x: _sec(x["pace"])) if eng else {"pace": "", "date": d["updated"]}
    last = eng[-1] if eng else best
    cur = next((w for w in d.get("year", []) if w.get("current")), None)
    return {
        "start_marathon": d["start"]["marathon"], "start_date_long": long_(d["start"]["date"]),
        "start_date_short": short(d["start"]["date"]),
        "now_marathon": d["now"]["marathon"], "now_date_long": long_(d["now"]["date"]),
        "now_date_short": short(d["now"]["date"]),
        "threshold_best": best["pace"], "threshold_best_month": month(best["date"]),
        "threshold_now": last["pace"], "threshold_now_month": month(last["date"]),
        "half_pr": (d.get("half_pr") or {}).get("time", ""),
        "half_pr_month": month((d.get("half_pr") or {}).get("date", d["updated"])),
        "week_plan_miles": str(cur["plan"]) if cur else "",
        "data_date": d["updated"],
    }


PH = re.compile(r"\{([a-z_]+)\}")


def fill(obj, F, used):
    if isinstance(obj, str):
        def rep(m):
            k = m.group(1)
            if k not in F:
                raise SystemExit(f"unknown placeholder {{{k}}} in pages/questions.json")
            used.add(k)
            return F[k]
        return PH.sub(rep, obj)
    if isinstance(obj, list):
        return [fill(x, F, used) for x in obj]
    if isinstance(obj, dict):
        return {k: (fill(v, F, used) if k not in ("slug", "updated", "published") else v) for k, v in obj.items()}
    return obj


def live_questions(qs):
    F = facts()
    sp = ROOT / "pages" / ".facts-state.json"
    state = json.loads(sp.read_text()) if sp.exists() else {}
    out = []
    for q in qs:
        used = set()
        fq = fill(q, F, used)
        h = hashlib.sha256(json.dumps({k: F[k] for k in sorted(used)}).encode()).hexdigest()[:16]
        prev = state.get(q["slug"])
        if prev and prev["hash"] != h:          # one of this page's numbers changed
            prev = {"hash": h, "updated": max(q["updated"], F["data_date"])}
        elif not prev:                           # first build: keep the hand-set date
            prev = {"hash": h, "updated": q["updated"]}
        fq["updated"] = max(q["updated"], prev["updated"])
        state[q["slug"]] = prev
        out.append(fq)
    sp.write_text(json.dumps(state, indent=1) + "\n")
    return out

def main():
    eps = json.loads((ROOT / "episodes" / "episodes.json").read_text())
    eps.sort(key=lambda e: e["number"])
    data_date = json.loads((ROOT / "data" / "progress.json").read_text())["updated"]
    urls = [("/", "weekly", data_date), ("/episodes/", "weekly", max([e["date"] for e in eps] or ["2026-11-18"])),
            ("/ai-running-coach/", "monthly", "2026-11-18")]
    (ROOT / "episodes").mkdir(exist_ok=True)
    (ROOT / "episodes" / "index.html").write_text(episodes_index(eps))
    for e in eps:
        d = ROOT / "episodes" / e["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(episode_page(e))
        urls.append((f"/episodes/{e['slug']}/", "monthly", e["date"]))
    qs = live_questions(json.loads((ROOT / "pages" / "questions.json").read_text()))
    for q in qs:
        d = ROOT / q["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(question_page(q, qs))
        urls.append((f"/{q['slug']}/", "monthly", q["updated"]))
    d = ROOT / "ai-running-coach"
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(coach_page(qs))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{SITE}{u}</loc><lastmod>{m}</lastmod><changefreq>{f}</changefreq></url>" for u, f, m in urls]
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n")
    (ROOT / "robots.txt").write_text(ROBOTS.format(site=SITE))
    print(f"built {len(eps)} episode page(s), episodes index, ai-running-coach, sitemap ({len(urls)} urls), robots.txt")


if __name__ == "__main__":
    main()
