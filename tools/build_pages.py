#!/usr/bin/env python3
"""build_pages.py: builds the SEO pages for tothefinish.ai from episodes/episodes.json.

Tyler 2026-11-18: "Should we go for an SEO play on the website" -> "Build". The plan
(Brain: brain/methods/social/growth-playbook.md + brain/social/automation.md): one page per
episode (the video, a short write-up in Tyler's voice, one search phrase, the sign-up form,
VideoObject structured data), an episodes index, the "how the coaches decide" page, sitemap.xml and
robots.txt. Homepage prose stays hand-edited; this script refreshes shared asset versions
and bakes dated progress values from data/progress.json into index.html.

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
from zoneinfo import ZoneInfo
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://tothefinish.ai"
GTM = "GTM-5Q6Q2KFL"
TODAY = dt.datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()


def asset_ver():
    """Short hash of the shared CSS and JS, added as ?v= so browsers fetch a changed file at once."""
    import hashlib
    h = hashlib.sha1()
    for f in ("site.css", "ui.css", "motion.css", "motion.js", "join.js", "races.js", "charts.js", "coaches-page.js", "feed.js",
              "episode-live.js", "watch-story.css", "watch-story.js", "training.css", "training.js", "coaching-interest.css"):
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


def head(title, desc, path, extra="", index=True, share_image=None):
    share_image = share_image or SITE + "/assets/og.jpg"
    canon = (f'<link rel="canonical" href="{SITE}{path}">' if index else '')
    crumbs = []
    if path != "/" and index:
        crumbs = [("Home", "/")]
        if path.startswith("/episodes/") and path != "/episodes/":
            crumbs.append(("Episodes", "/episodes/"))
        label = title.split(" | ")[0].split(" · ")[0]
        crumbs.append((label, path))
        extra += ld({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":i+1,"name":label,"item":SITE+url} for i,(label,url) in enumerate(crumbs)]})
    trail = '<nav class="breadcrumbs" aria-label="Breadcrumb">' + ' <span aria-hidden="true">/</span> '.join(
        f'<a href="{esc(url)}">{esc(label)}</a>' if i<len(crumbs)-1 else f'<span aria-current="page">{esc(label)}</span>'
        for i,(label,url) in enumerate(crumbs)) + '</nav>' if crumbs else ''
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
<meta property="og:image" content="{esc(share_image)}">
<meta property="og:site_name" content="To The Finish">
<meta property="og:image:alt" content="{esc(title)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:type" content="{ogtype}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{esc(share_image)}">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="robots" content="{'index,follow,max-image-preview:large,max-video-preview:-1' if index else 'noindex'}">
<link rel="icon" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preload" as="font" type="font/woff2" href="/assets/barlow-condensed-800.woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css?v={VER}">
<link rel="stylesheet" href="/assets/ui.css?v={VER}">
<link rel="stylesheet" href="/assets/motion.css?v={VER}">
{extra}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<main id="main">
<header class="page-top">
  <div class="wrap">
    <div class="bar">
      <a class="mark" href="/">TO THE <span class="o">FINISH.</span></a>
      {site_nav(path)}
    </div>
    {trail}
"""


FORM = """<form class="join" action="https://app.kit.com/forms/10209840/subscriptions" method="post" id="join-{id}">
  <label>First name <span>(optional)</span><input name="fields[first_name]" autocomplete="given-name"></label>
  <label>Email<input name="email_address" type="email" required autocomplete="email"></label>
  <button type="submit">{button}</button>
</form>
<p class="fine">One email a week: my miles, what went sideways, and the new episode when one’s out. Free, and you can leave any time. You’ll confirm on Kit’s page. <a href="/privacy/">How I use your email</a>.</p>"""

FOOT = "</main>\n" + site_footer() + """
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
Sitemap: {site}/video-sitemap.xml
"""


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


def episode_poster(e):
    return SITE + e["poster"] if e.get("poster", "").startswith("/") else e.get("poster") or f'https://i.ytimg.com/vi/{e["youtube_id"]}/hqdefault.jpg'


def duration_label(e):
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", e.get("duration", ""))
    if not m:
        return "Watch episode"
    h, minutes, seconds = (int(x or 0) for x in m.groups())
    return f"{h*60+minutes}:{seconds:02d}"


def episode_page(e):
    path = f"/episodes/{e['slug']}/"
    title = f"{e['title']}: Episode {e['number']} | To The Finish, the animated series"
    thumb = episode_poster(e)
    embed = f"https://www.youtube-nocookie.com/embed/{e['youtube_id']}"
    video = {
        "@context":"https://schema.org", "@type":"VideoObject", "@id":SITE+path+"#video",
        "name":f"The Hiring | To The Finish, Episode {e['number']}" if e['number']==1 else f"{e['title']} | To The Finish, Episode {e['number']}",
        "description":e["description"], "thumbnailUrl":[thumb],
        "uploadDate":e.get("published_at",e["date"]), "embedUrl":embed,
        "url":SITE+path, "mainEntityOfPage":SITE+path, "inLanguage":"en",
        "creator":{"@type":"Person","@id":SITE+"/#tyler","name":"Tyler Stewart","url":SITE+"/#tyler"},
        "partOfSeries":{"@type":"CreativeWorkSeries","@id":SITE+"/#series","name":"To The Finish","url":SITE+"/"}}
    if e.get("duration"): video["duration"] = e["duration"]
    if e.get("video_file"): video["contentUrl"] = SITE + e["video_file"]
    player = f'<iframe src="{esc(embed)}" title="Watch {esc(e["title"])}" loading="eager" referrerpolicy="strict-origin-when-cross-origin" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>'
    if e.get("video_file"):
        track = f'<track kind="captions" src="{esc(e["captions"])}" srclang="en" label="English" default>' if e.get("captions") else ''
        player = f'<video controls playsinline preload="none" poster="{esc(e.get("poster",thumb))}" aria-label="{esc(e["title"])}: Episode {e["number"]}"><source src="{esc(e["video_file"])}" type="video/mp4">{track}<p><a href="https://www.youtube.com/watch?v={esc(e["youtube_id"])}">Watch on YouTube</a></p></video>'
    transcript = f'<p class="fine">English captions are available in the video controls. <a href="{esc(e["captions"])}" download>Download captions</a>.</p>' if e.get("captions") else ""
    body = "".join(f"<p>{esc(p)}</p>" for p in e.get("writeup", []))
    garmin = f'<p class="note">From my Garmin: {esc(e["garmin"])}</p>' if e.get("garmin") else ""
    date_h = dt.date.fromisoformat(e["date"]).strftime("%B %-d, %Y")
    behind = 'The gap on <span class="o">day one.</span>' if e["number"] == 1 else 'The training <span class="o">behind it.</span>'
    vclass = "video vertical" if e.get("vertical") else "video"
    return head(title,e["description"],path,ld(video),share_image=thumb) + f"""
  </div>
</header>
<section class="episode-stage">
  <div class="wrap watch-layout">
    <div class="watch-screen">
      <div class="{vclass}">{player}</div>
      <a class="player-fallback" href="https://www.youtube.com/watch?v={esc(e['youtube_id'])}">Open in YouTube <span aria-hidden="true">↗</span></a>
    </div>
    <div class="watch-intro">
      <p class="kicker">Episode {e['number']} · {duration_label(e)}</p>
      <h1 class="display">{esc(e['title'])}</h1>
      <p class="lead">{esc(e['description'])}</p>
      <p class="fine">Published <time datetime="{e['date']}">{date_h}</time> · By <a href="/#tyler">Tyler Stewart</a></p>
      <p class="fine">Animated AI characters and voices. My real training.</p>
      <a class="more" href="#behind-episode">The real numbers behind it <span aria-hidden="true">↓</span></a>
    </div>
  </div>
</section>
<section id="behind-episode"><div class="wrap episode-notes">
  <div><p class="kicker">Behind the episode</p><h2 class="display">{behind}</h2><a class="more" href="/#progress">Where I am now →</a></div>
  <div class="prose">{body}{garmin}{transcript}<p><a href="/how-the-coaches-decide/">How the coaches decide</a> · <a href="/episodes/">All episodes</a></p></div>
</div></section>
<section><div class="wrap letter-layout">
  <div><p class="kicker">The Sunday letter</p><h2 class="display">The next week<br><span class="o">of the chase.</span></h2><p class="body">My miles, the coaches’ calls and the new episode when one’s out.</p></div>
  <div>{FORM.format(id='ep',button='Get the Sunday letter')}</div>
</div></section>
""" + FOOT


def episodes_index(eps):
    path = "/episodes/"
    desc = "Watch To The Finish, the animated series. A dad who started at 258 lb created five AI coaches for a sub-3 marathon. Start with Episode 1: The Hiring."
    cards = []
    for e in reversed(eps):
        cards.append(f'''<li><a class="episode-card" href="/episodes/{esc(e['slug'])}/">
          <div class="episode-art"><img src="{esc(e.get('poster',episode_poster(e)))}" alt="A scene from {esc(e['title'])}" width="540" height="960" loading="{'eager' if e==eps[-1] else 'lazy'}"><span class="play-disc" aria-hidden="true">▶</span></div>
          <div class="episode-card-copy"><p class="kicker">Episode {e['number']} · {duration_label(e)}</p><h2 class="display">{esc(e['title'])}</h2><p>{esc(e['description'])}</p><span class="episode-play">Watch episode <span aria-hidden="true">→</span></span><p class="fine"><time datetime="{e['date']}">{dt.date.fromisoformat(e['date']).strftime('%B %-d, %Y')}</time></p></div>
        </a></li>''')
    series = {"@context":"https://schema.org","@type":"CollectionPage","name":"To The Finish episodes","url":SITE+path,
        "mainEntity":{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":SITE+f"/episodes/{e['slug']}/","name":e['title']} for i,e in enumerate(reversed(eps))]}}
    return head("Watch the episodes | To The Finish, the animated series",desc,path,ld(series)) + f'''<div class="page archive-head">
      <p class="kicker">Season 1 · The 5K</p><h1 class="display">Start before<br><span class="o">the first mile.</span></h1>
      <p class="lead">I asked for a sub-3 marathon. Before the first run, the coaches had to agree on tomorrow.</p>
    </div></div></header>
<section class="archive-stage"><div class="wrap"><ol class="episode-list">{''.join(cards)}</ol>
<p class="fine">The episodes use the numbers from when they were made. <a href="/#progress">Today’s progress is here</a>.</p></div></section>
<section><div class="wrap letter-layout"><div><p class="kicker">The Sunday letter</p><h2 class="display">There’s a week<br><span class="o">between the scenes.</span></h2><p class="body">That’s what I write about on Sundays, with the new episode when one’s out.</p></div><div>{FORM.format(id='idx',button='Get the Sunday letter')}</div></div></section>
''' + FOOT


def coach_page(qs=()):
    path = "/how-the-coaches-decide/"
    desc = ("Five AI coaches argue over one dad's training: running, strength, nutrition, recovery and a head coach who settles "
            "it when they disagree. How the cast of To The Finish decides my week on the way to a sub-3 marathon.")
    org = {"@context": "https://schema.org", "@type": "WebPage", "name": "How the coaches decide | To The Finish",
           "url": SITE + path, "description": desc}
    return head("How the coaches decide | To The Finish, the animated series", desc, path, ld(org)) + """    <div class="page">
      <p class="kicker">The coaches</p>
      <h1 class="display">How the coaches <span class="o">decide.</span></h1>
      <p class="lead">Five AI coaches plan my training, and they argue about it. They have one runner, and it's me. I started at 258 lb and I'm training for a sub-3 marathon at Chicago on October 10, 2027.</p>
    </div>
  </div>
</header>
<section>
  <div class="wrap prose">
    <h2>Who does what</h2>
    <p><b>Kai</b> plans every run from my Garmin data. He's usually facing east before the sun is up, already talking about the hill. His one law: easy days stay easy, even when I don't want them to.</p>
    <p><b>Bo</b> fits short, heavy lifts around the running. He laughs louder than anyone and leaves chalk on everything, and he'll cut his own session short to protect a long run.</p>
    <p><b>Juno</b> plans every meal around the training. She's quick and she teases, and she has no patience at all for me skipping breakfast before a hard run.</p>
    <p><b>Mo</b> watches my recovery. He carries a roll of tape and a lacrosse ball, asks one precise question, and never clears pain to train.</p>
    <p><b>Rook</b> is the head coach. When the others want different things from the same week, he says one line, and that's the call.</p>
    <h2>When the coaches disagree</h2>
    <p>Rook settles every clash in the same order. What I say and any pain I report come first, then the race in Chicago, then my weight, then strength. So when Bo wants heavy legs the day before a hard run, the run wins, and Bo takes it better than you'd think.</p>
    <p>The plan comes from the research. Every change is written down with the rule behind it. The coaches are AI characters, and this is my personal setup, not medical or nutrition advice.</p>
    <h2>What a number can’t tell them</h2>
    <p>A slower pace can mean a hill, a walk or a tired runner. They have to read the pace, cadence and terrain together. They still need me to report pain. A watch estimate is evidence to check, never a race result or a promise that I’m ready.</p>
    <p><a href="/coaches/">Read each coach’s data and latest call</a></p>
    <h2>Questions people ask</h2>
    <ul class="qlist">""" + "".join(f'<li><a href="/{q["slug"]}/">{esc(q["question"])}</a></li>' for q in qs) + """</ul>
  </div>
</section>
<link rel="stylesheet" href="/assets/watch-story.css?v=""" + VER + """">
""" + (ROOT / "pages/how-it-works.html").read_text() + """
<script src="/assets/watch-story.js?v=""" + VER + """" defer></script>
<section>
  <div class="wrap">
    <p class="kicker">The Sunday letter</p>
    """ + FORM.format(id='coach', button='Get the Sunday letter') + """
    <p class="body" style="margin-top:22px"><a href="/episodes/">Watch the episodes</a></p>
  </div>
</section>
""" + FOOT


def privacy_page():
    path = "/privacy/"
    desc = ("What tothefinish.ai collects for the Sunday letter, where it goes, "
            "and how to get off the list.")
    page = {"@context": "https://schema.org", "@type": "WebPage", "name": "Privacy | To The Finish",
            "url": SITE + path, "description": desc}
    return head("Privacy | To The Finish", desc, path, ld(page)) + """    <div class="page">
      <p class="kicker">Updated November 26, 2026</p>
      <h1 class="display">Privacy, in <span class="o">plain words.</span></h1>
      <p class="lead">This is a one-person site. Here's what it collects and where that goes.</p>
    </div>
  </div>
</header>
<section>
  <div class="wrap prose">
    <h2>What the forms collect</h2>
    <p>The Sunday letter form asks for your email and an optional first name. From November 24 to 26 the site also had an AI coaching interest form. It’s closed now. If you joined it, you can leave the same way as the letter, below. Please don’t send medical records through the form.</p>
    <h2>Where it goes</h2>
    <p>The forms send what you enter to Kit, the email service I use. The closed coaching interest list was kept separate from the Sunday letter, and joining one never signed you up for the other.</p>
    <h2>What the site counts</h2>
    <p>The site uses Google Analytics to count visits, watch-link clicks and requests for the Sunday letter; a form submission doesn’t tell me whether an email was delivered. It sets a cookie to tell one visit from the next. Your name, your email and anything you type are never sent to it. Episode 1 plays directly on this site. You can also open it on YouTube.</p>
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


AUTHOR = {"@type":"Person", "@id":SITE+"/#tyler", "name":"Tyler Stewart", "url":SITE+"/#tyler"}


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
    return head(q["title"] + " | To The Finish", q["description"], path, ld(art)) + f"""    <div class="page">
      <p class="kicker">Updated {upd}</p>
      <h1 class="display" style="font-size:clamp(40px,6.5vw,76px)">{esc(q['question'])}</h1>
    </div>
  </div>
</header>
<section>
  <div class="wrap prose">{out}
    <p class="note">By <a href="/#tyler" rel="author">Tyler Stewart</a>. Numbers from my Garmin (chest-strap heart rate). Not medical or nutrition advice; the coaches are AI characters.</p>
  </div>
</section>
<section>
  <div class="wrap">
    <p class="kicker">The Sunday letter</p>
    {FORM.format(id='q', button='Get the Sunday letter')}
    <div class="prose" style="margin-top:26px"><h2>More questions</h2><ul class="qlist">{others}<li><a href="/how-the-coaches-decide/">How the coaches decide</a></li><li><a href="/chicago-marathon-2027/">Chicago Marathon 2027: dates, lottery and qualifying times</a></li><li><a href="/san-diego-races/">Upcoming San Diego races</a></li></ul></div>
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

# Old addresses (2026-11-22, Tyler: "Yes lean into the change"): the show is an animated series, so the pages named
# for a running coach moved. The old address forwards to the new one.
MOVED = {"story": "/", "coaching": "/how-the-coaches-decide/", "ai-running-coach": "/how-the-coaches-decide/",
         "ai-running-coach-for-heavier-runners": "/training-for-a-marathon-from-258-lb/"}


def moved_page(new):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>To The Finish</title>'
            f'<link rel="canonical" href="{SITE}{new}"><meta http-equiv="refresh" content="0; url={new}">'
            f'</head><body><p><a href="{new}">This page moved.</a></p></body></html>\n')


def main():
    eps = json.loads((ROOT / "episodes" / "episodes.json").read_text())
    eps = [e for e in eps if e.get("youtube_id") and e["youtube_id"] != "TBD" and e["date"] <= TODAY]
    eps.sort(key=lambda e: e["number"])
    data_date = json.loads((ROOT / "data" / "progress.json").read_text())["updated"]
    urls = [("/", "weekly", data_date), ("/episodes/", "weekly", max([e["date"] for e in eps] or ["2026-11-18"])),
            ("/how-the-coaches-decide/", "monthly", "2026-11-23"), ("/coaches/", "weekly", data_date)]
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
        urls.append((f"/episodes/{e['slug']}/", "monthly", e.get("updated",e["date"])))
    qs = live_questions(json.loads((ROOT / "pages" / "questions.json").read_text()))
    for q in qs:
        d = ROOT / q["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(question_page(q, qs))
        urls.append((f"/{q['slug']}/", "monthly", q["updated"]))
    d = ROOT / "how-the-coaches-decide"
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(coach_page(qs))
    for old, new in MOVED.items():
        d = ROOT / old
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(moved_page(new))
    d = ROOT / "privacy"
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(privacy_page())
    urls.append(("/privacy/", "yearly", "2026-11-23"))
    (ROOT / "404.html").write_text(notfound_page())
    home = ROOT / "index.html"
    h = home.read_text()
    h = re.sub(r'(/assets/(?:ui\.css|motion\.css|motion\.js|join\.js|charts\.js|episode-live\.js|watch-story\.css|watch-story\.js|training\.css|training\.js|coaching-interest\.css))(\?v=\w+)?"', lambda m: f'{m.group(1)}?v={VER}"', h)
    D = json.loads((ROOT / "data/progress.json").read_text())
    date = dt.date.fromisoformat(D["updated"])
    week = next((w for w in D.get("year",[]) if w.get("current")),{})
    gap = int(round(D["to_go_s"]))
    full = lambda iso: dt.date.fromisoformat(iso).strftime("%b %-d, %Y")
    values = {"now":D["now"]["marathon"], "nowdate":full(D["now"]["date"]),
        "start":D["start"]["marathon"], "startdate":full(D["start"]["date"]), "asof":date.strftime("%b %-d"),
        "togo":f"{gap//3600}:{gap%3600//60:02d}:{gap%60:02d}",
        "weeksleft":max(0,(dt.date(2027,10,10)-dt.date.fromisoformat(TODAY)).days//7),
        "wkdone":week.get("done") if week.get("done") is not None else "Not recorded", "wkplan":week.get("plan","Not set")}
    for key,value in values.items():
        h=re.sub(r'(<[^>]+data-k="'+key+r'"[^>]*>)[^<]*(</[^>]+>)',lambda m:m[1]+esc(str(value))+m[2],h)
    h=re.sub(r'The saved numbers above are from [A-Z][a-z]{2} \d{1,2};',f'The saved numbers above are from {date.strftime("%b %-d")};',h)
    home.write_text(h)
    # Publication dates describe the video, not the day a generator ran.
    vs = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">']
    for e in eps:
        content = f'<video:content_loc>{SITE}{esc(e["video_file"])}</video:content_loc>' if e.get("video_file") else ""
        vs.append(f'<url><loc>{SITE}/episodes/{esc(e["slug"])}/</loc><video:video><video:thumbnail_loc>{esc(episode_poster(e))}</video:thumbnail_loc><video:title>{esc(e["title"])}</video:title><video:description>{esc(e["description"])}</video:description><video:player_loc>https://www.youtube-nocookie.com/embed/{esc(e["youtube_id"])}</video:player_loc>{content}<video:publication_date>{esc(e.get("published_at",e["date"]))}</video:publication_date></video:video></url>')
    # The homepage explainer is a separate film, not a numbered episode.
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        for video in json.loads(block).get('@graph', []):
            if video.get('@type') != 'VideoObject':
                continue
            thumbnail = video['thumbnailUrl']
            if isinstance(thumbnail, list):
                thumbnail = thumbnail[0]
            vs.append(f'<url><loc>{SITE}/</loc><video:video><video:thumbnail_loc>{esc(thumbnail)}</video:thumbnail_loc><video:title>{esc(video["name"])}</video:title><video:description>{esc(video["description"])}</video:description><video:content_loc>{esc(video["contentUrl"])}</video:content_loc><video:publication_date>{esc(video["uploadDate"])}</video:publication_date><video:duration>69</video:duration></video:video></url>')
    vs.append('</urlset>')
    (ROOT/'video-sitemap.xml').write_text('\n'.join(vs)+'\n')
    from build_training import main as build_training
    training_date = build_training()
    urls.append(("/training/", "daily", training_date))
    # /coaching/ closed 2026-11-26 (Gerben, Bare, Hormozi and Godin audits; Tyler: "No wait list unless I am truly needed"):
    # nothing under the To The Finish name offers coaching. It redirects through MOVED; build_coaching_interest stays for a separately named product.
    # Revision dates persist across routine data refreshes; never pretend each build is a new article.
    revisions = json.loads((ROOT/'pages/seo-revisions.json').read_text())
    urls = [(u,f,max(m,revisions.get(u,m))) for u,f,m in urls]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{SITE}{u}</loc><lastmod>{m}</lastmod><changefreq>{f}</changefreq></url>" for u, f, m in urls]
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n")
    (ROOT / "robots.txt").write_text(ROBOTS.format(site=SITE))
    print(f"built {len(eps)} episode page(s), episodes index, how-the-coaches-decide, sitemap ({len(urls)} urls), robots.txt")


if __name__ == "__main__":
    main()
