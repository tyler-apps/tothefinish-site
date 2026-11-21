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
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://tothefinish.ai"
GTM = "GTM-5Q6Q2KFL"
TODAY = dt.date.today().isoformat()


def asset_ver():
    """Short hash of the shared CSS and JS, added as ?v= so browsers fetch a changed file at once."""
    import hashlib
    h = hashlib.sha1()
    for f in ("site.css", "ui.css", "motion.css", "motion.js", "join.js", "races.js", "charts.js", "coaches-page.js",
              "episode-live.js"):
        p = ROOT / "assets" / f
        if p.exists():
            h.update(p.read_bytes())
    return h.hexdigest()[:8]


VER = asset_ver()


def esc(s):
    return html.escape(s or "", quote=True)


# One nav and one footer for the whole site (2026-11-21 review: the built pages had drifted from the home page).
# Both are read from the hand-edited index.html; build_coaches.py uses the same two helpers.
_HOME = (ROOT / "index.html").read_text()
_NAV = re.search(r'<nav class="nav" aria-label="Main">.*?</nav>', _HOME, re.S).group(0)
_MNAV = re.search(r'<details class="mnav">.*?</details>', _HOME, re.S).group(0)
_FOOTER = re.search(r"<footer>.*?</footer>", _HOME, re.S).group(0)


def site_nav(path=""):
    """The desktop nav and the phone menu, with the current page marked."""
    out = _NAV + "\n      " + _MNAV
    return out.replace(f'<a href="{path}">', f'<a href="{path}" aria-current="page">') if path else out


def site_footer():
    return _FOOTER


def head(title, desc, path, extra="", index=True):
    canon = (f'<link rel="canonical" href="{SITE}{path}">' if index else '<meta name="robots" content="noindex">')
    ogtype = "article" if '"@type": "Article"' in extra else "website"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script async src="https://www.googletagmanager.com/gtm.js?id={GTM}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());</script>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{canon}
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/assets/og.jpg">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:type" content="{ogtype}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/assets/og.jpg">
<link rel="icon" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preload" as="font" type="font/woff2" href="/assets/barlow-condensed-800.woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css?v={VER}">
<link rel="stylesheet" href="/assets/ui.css?v={VER}">
<link rel="stylesheet" href="/assets/motion.css?v={VER}">
{extra}
</head>
<body>
<header class="page-top">
  <div class="wrap">
    <div class="bar">
      <a class="mark" href="/">TO THE <span class="o">FINISH.</span></a>
      {site_nav(path)}
    </div>
"""


FORM = """<form class="join" action="https://app.kit.com/forms/10209840/subscriptions" method="post" id="join-{id}" data-thanks="thanks-{id}">
  <input name="fields[first_name]" aria-label="First name" placeholder="First name" autocomplete="given-name">
  <input name="email_address" type="email" aria-label="Email" placeholder="Email" required autocomplete="email">
  <button type="submit">{button}</button>
</form>
<div class="thanks" id="thanks-{id}">You're in. The first letter comes Sunday night.</div>
<p class="fine">The Sunday letter is one email a week: my miles, what went sideways, and the new episode when one's out.</p>"""

FOOT = site_footer() + """
<iframe name="hidden_iframe" id="hidden_iframe" style="display:none" title="form target"></iframe>
<script src="/assets/join.js?v=VERSION"></script>
<script src="/assets/motion.js?v=VERSION" defer></script>
</body>
</html>
""".replace("VERSION", VER)


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
    <p class="kicker">The Sunday letter</p>
    <h2 class="display" style="font-size:clamp(40px,6vw,64px);margin-bottom:18px">Get the next episode <span class="o">when it's out.</span></h2>
    {FORM.format(id='ep', button='Get the Sunday letter')}
    <p class="body" style="margin-top:22px"><a href="/episodes/">All episodes</a></p>
  </div>
</section>
""" + FOOT


def episodes_index(eps):
    path = "/episodes/"
    desc = ("Every episode of To The Finish, the AI running coach show: a 258 lb dad of two training for a sub-3 marathon at Chicago, "
            "coached by five AI coaches, with the real numbers from his Garmin.")
    if eps:
        items = "".join(
            f'<li><a href="/episodes/{e["slug"]}/"><span class="n">Episode {e["number"]} · '
            f'{dt.date.fromisoformat(e["date"]).strftime("%b %-d, %Y")}</span><h3>{esc(e["title"])}</h3>'
            f'<p>{esc(e["description"])}</p></a></li>' for e in reversed(eps))
        listing = f'<ul class="eplist">{items}</ul>'
    else:
        listing = '<p class="body">Episode 1 comes out Sunday, November 22. It&#x27;s the week the coaches got hired, and the first time they disagreed about me.</p>'
    series = {"@context": "https://schema.org", "@type": "CreativeWorkSeries", "name": "To The Finish",
              "url": SITE + "/", "description": desc}
    return head("Episodes | To The Finish, the AI running coach show", desc, path, ld(series)) + f"""    <div class="page">
      <p class="kicker">Season 1: The 5K</p>
      <h1 class="display">The <span class="o">episodes.</span></h1>
      <p class="lead">Two episodes a month, on Sundays, from the first week of training to the start line in Chicago. Each one comes from the weeks that really happened, with the times straight off my watch, including the runs that went sideways.</p>
      <p class="eptop"><a class="btn" href="https://www.youtube.com/@tothefinishai">Watch on YouTube</a></p>
    </div>
  </div>
</header>
<section>
  <div class="wrap">
    {listing}
    <div style="margin-top:36px">{FORM.format(id='idx', button='Get the Sunday letter')}</div>
  </div>
</section>
""" + FOOT


def coach_page(qs=()):
    path = "/ai-running-coach/"
    desc = ("My AI running coach is a team of five: running, strength, nutrition, recovery and a head coach who settles "
            "it when they disagree. It reads my Garmin data and plans my week toward a sub-3 marathon.")
    org = {"@context": "https://schema.org", "@type": "WebPage", "name": "AI running coach | To The Finish",
           "url": SITE + path, "description": desc}
    return head("AI Running Coach: five coaches, one sub-3 attempt | To The Finish", desc, path, ld(org)) + """    <div class="page">
      <p class="kicker">The coaches</p>
      <h1 class="display">My AI running <span class="o">coach.</span></h1>
      <p class="lead">My AI running coach is a team of five, and they argue. Right now they coach one runner: me. I started at 258 lb and I'm training for a sub-3 marathon at Chicago on October 10, 2027.</p>
    </div>
  </div>
</header>
<section>
  <div class="wrap prose">
    <h2>Who does what</h2>
    <p><b>Kai</b> plans every run from my Garmin data. He's usually facing east before the sun is up, already talking about the hill. His one law: easy days stay easy, even when I don't want them to.</p>
    <p><b>Bo</b> fits short, heavy lifts around the running. He laughs louder than anyone and leaves chalk on everything, and he'll cut his own session short to protect a long run.</p>
    <p><b>Juno</b> plans every meal around the training. She's quick and she teases, and she has no patience at all for me skipping breakfast before a hard run.</p>
    <p><b>Mo</b> keeps me in one piece. He carries a roll of tape and a lacrosse ball, asks one precise question, and never clears pain to train.</p>
    <p><b>Rook</b> is the head coach. When the others want different things from the same week, he moves a card on the board, says one line, and that's the call.</p>
    <h2>How it decides</h2>
    <p>Rook settles every clash in the same order. Pain I report comes first, then the race in Chicago, then my weight, then strength. So when Bo wants heavy legs the day before a hard run, the run wins, and Bo takes it better than you'd think.</p>
    <p>The plan comes from the research and from coaching methods that have built real marathoners. Every change is written down with the rule behind it. The coaches are AI characters, and this is my personal setup, not medical or nutrition advice.</p>
    <h2>Questions people ask</h2>
    <ul class="qlist">""" + "".join(f'<li><a href="/{q["slug"]}/">{esc(q["question"])}</a></li>' for q in qs) + """</ul>
    <h2>Can I use it?</h2>
    <p>Not yet. It has to get me to Chicago first. If it does, the people on the waitlist are next.</p>
  </div>
</section>
<section>
  <div class="wrap">
    <form class="join" action="https://app.kit.com/forms/10209840/subscriptions" method="post" id="join-coach" data-thanks="thanks-coach">
      <input name="fields[first_name]" aria-label="First name" placeholder="First name" autocomplete="given-name">
      <input name="email_address" type="email" aria-label="Email" placeholder="Email" required autocomplete="email">
      <input class="wide" name="fields[training_for]" aria-label="Your race and date" placeholder="What are you training for? (race and date)">
      <button type="submit">Get on the waitlist</button>
    </form>
    <div class="thanks" id="thanks-coach">You're on the waitlist. If the coaches get me to Chicago, you're first to try them.</div>
    <p class="body" style="margin-top:22px"><a href="/episodes/">Watch the episodes</a></p>
  </div>
</section>
""" + FOOT


def privacy_page():
    path = "/privacy/"
    desc = ("What tothefinish.ai collects when you sign up for the Sunday letter or the waitlist, where it goes, "
            "and how to get off the list.")
    page = {"@context": "https://schema.org", "@type": "WebPage", "name": "Privacy | To The Finish",
            "url": SITE + path, "description": desc}
    return head("Privacy | To The Finish", desc, path, ld(page)) + """    <div class="page">
      <p class="kicker">Updated November 21, 2026</p>
      <h1 class="display">Privacy, in <span class="o">plain words.</span></h1>
      <p class="lead">This is a one-person site. Here's what it collects and where that goes.</p>
    </div>
  </div>
</header>
<section>
  <div class="wrap prose">
    <h2>What the forms collect</h2>
    <p>The Sunday letter form asks for your first name and your email. The waitlist form asks for the same two, plus the race you're training for. That's all the forms ask for.</p>
    <h2>Where it goes</h2>
    <p>The forms send what you type to Kit, the email service I use to send the Sunday letter. I read the race you wrote so I know who I'm building this for.</p>
    <h2>What the site counts</h2>
    <p>The site uses Google Analytics to count visits and sign-ups, and which race gets picked on the San Diego list. It sets a cookie to tell one visit from the next. Your name, your email and anything you type are never sent to it. Episode pages play the video through YouTube.</p>
    <h2>Getting off the list</h2>
    <p>Every email has an unsubscribe link at the bottom. Or write to <a href="mailto:hello@tothefinish.ai">hello@tothefinish.ai</a> and I'll take you off and delete what you sent.</p>
    <h2>The coaches</h2>
    <p>Rook, Kai, Bo, Juno and Mo are AI characters. This is my personal coaching setup, and nothing here is medical or nutrition advice.</p>
    <h2>Questions</h2>
    <p>Write to <a href="mailto:hello@tothefinish.ai">hello@tothefinish.ai</a>.</p>
  </div>
</section>
""" + FOOT


def notfound_page():
    desc = "There's no page at this address on tothefinish.ai."
    return head("Page not found | To The Finish", desc, "/404.html", index=False) + """    <div class="page">
      <p class="kicker">404</p>
      <h1 class="display">Wrong <span class="o">turn.</span></h1>
      <p class="lead">There's no page at this address. The home page has the whole story, and the coaches page has today's numbers.</p>
      <p><a class="btn" href="/">Back to the start</a></p>
      <p class="body" style="margin-top:22px"><a href="/coaches/">The coaches</a> · <a href="/episodes/">Episodes</a> · <a href="/races/">My races</a></p>
    </div>
  </div>
</header>
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
            th = "".join(f'<th scope="col">{esc(c)}</th>' for c in rows[0])
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
    <p class="kicker">The Sunday letter</p>
    {FORM.format(id='q', button='Get the Sunday letter')}
    <div class="prose" style="margin-top:26px"><h2>More questions</h2><ul class="qlist">{others}<li><a href="/ai-running-coach/">How my AI running coach works</a></li><li><a href="/chicago-marathon-2027/">Chicago Marathon 2027: dates, lottery and qualifying times</a></li><li><a href="/san-diego-races/">Upcoming San Diego races</a></li></ul></div>
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
            ("/ai-running-coach/", "monthly", "2026-11-18"), ("/coaches/", "weekly", data_date)]
    if (ROOT / "data" / "races.json").exists():
        urls.append(("/san-diego-races/", "weekly", json.loads((ROOT / "data" / "races.json").read_text())["updated"]))
    urls.append(("/chicago-marathon-2027/", "weekly", data_date))
    from build_race_reports import report_urls   # /races/ and one report per race run (built by build_race_reports.py)
    urls += [(u, "weekly", m) for u, m in report_urls(json.loads((ROOT / "data" / "progress.json").read_text()))]
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
    d = ROOT / "privacy"
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(privacy_page())
    urls.append(("/privacy/", "yearly", "2026-11-21"))
    (ROOT / "404.html").write_text(notfound_page())
    home = ROOT / "index.html"
    h = home.read_text()
    h = re.sub(r'(/assets/(?:ui\.css|motion\.css|motion\.js|join\.js|charts\.js|episode-live\.js))(\?v=\w+)?"', lambda m: f'{m.group(1)}?v={VER}"', h)
    home.write_text(h)
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{SITE}{u}</loc><lastmod>{m}</lastmod><changefreq>{f}</changefreq></url>" for u, f, m in urls]
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n")
    (ROOT / "robots.txt").write_text(ROBOTS.format(site=SITE))
    print(f"built {len(eps)} episode page(s), episodes index, ai-running-coach, sitemap ({len(urls)} urls), robots.txt")


if __name__ == "__main__":
    main()
