#!/usr/bin/env python3
"""build_chicago.py: builds /chicago-marathon-2027/ (Tyler 2026-11-19: "Yes, start Chicago").

Two halves: the official race facts (date, entry paths, fees, 2027 time-qualifier standards, course), read from
chicagomarathon.com/apply/ and /course/ on 2026-11-19 and kept in RACE below; and my own sub-3 build, filled from
data/progress.json (Garmin prediction, the plan's weeks and races), so the page moves every Sunday with the
progress refresh. Run by publish.sh after build_pages.py.

Searches it answers (DataForSEO, US monthly, 2026-11-19): chicago marathon 2027 14,800 · lottery 6,600 ·
qualifying time 4,400 · course map 6,600 · registration 2,900 · date 2,400 · charity 1,000 ·
training plan 480 · sub 3 marathon training plan 320.

    python3 tools/build_chicago.py
"""
import datetime as dt
import json
from pathlib import Path

from build_pages import FOOT, SITE, esc, head

ROOT = Path(__file__).resolve().parents[1]
PATH = "/chicago-marathon-2027/"
SRC_APPLY = "https://www.chicagomarathon.com/apply/"
SRC_COURSE = "https://www.chicagomarathon.com/course/"
CHECKED = "Nov 19, 2026"

# official facts, chicagomarathon.com, read 2026-11-19 (2027 standards are by age on race day)
STANDARDS = [("16 to 34", "2:50:00", "3:20:00"), ("35 to 39", "2:55:00", "3:25:00"), ("40 to 44", "3:00:00", "3:30:00"),
             ("45 to 49", "3:10:00", "3:40:00"), ("50 to 54", "3:15:00", "3:50:00"), ("55 to 59", "3:25:00", "3:55:00"),
             ("60 to 64", "3:40:00", "4:15:00"), ("65 to 69", "3:55:00", "4:30:00"), ("70 to 74", "4:15:00", "4:45:00"),
             ("75 to 79", "4:30:00", "5:00:00"), ("80 and over", "4:50:00", "5:20:00")]
ENTRY = [
    ("Drawing (lottery)", "Not guaranteed", "Applications ran Oct 8 to Oct 29, 2026. Results by email Tue Dec 8, 2026; pay by Tue Dec 15.", "Closed"),
    ("Time qualifier", "Guaranteed", "Run the standard for your age between Jan 1, 2025 and Oct 29, 2026.", "Closed"),
    ("Charity", "Guaranteed", "Raise money for an official charity. First come, first served until Fri Sep 10, 2027.", "Open"),
    ("Tour operator", "Guaranteed", "Through an official tour operator, from Tue Dec 8, 2026.", "TOUR"),
    ("Legacy", "Guaranteed", "For runners who finished five or more times in the last 10 years.", "Closed"),
]
FAQ = [
    ("When is the 2027 Chicago Marathon?", "Sunday, October 10, 2027. It starts and finishes in Grant Park."),
    ("When are the 2027 Chicago Marathon lottery results?", "Drawing results go out by email on Tuesday, December 8, 2026. Runners who get in pay by Tuesday, December 15."),
    ("What is the Chicago Marathon qualifying time?", "For 2027 it goes by your age on race day: 2:50 for men 16 to 34, 3:00 for men 40 to 44, 3:20 for women 16 to 34, 3:30 for women 40 to 44. The full table is above."),
    ("Can I still get into the 2027 Chicago Marathon?", "The drawing and time-qualifier windows are closed. Charity entries are open until September 10, 2027, and tour operators start December 8, 2026."),
    ("How much does the Chicago Marathon cost?", "$250 for US residents and $260 for everyone else, plus a processing fee. Charity entries are $325 and $335."),
    ("Is the Chicago Marathon course flat?", "The race calls it flat and fast. It runs through 29 neighborhoods, and the time limit is 6 hours 30 minutes, a 15-minute mile."),
]


def d(s):
    return dt.date.fromisoformat(s)


def nice(day):
    return f"{day:%a %b} {day.day}, {day.year}"


def main():
    prog = json.loads((ROOT / "data" / "progress.json").read_text())
    today = dt.date.today()
    race_day = dt.date(2027, 10, 10)
    weeks = (race_day - today).days // 7
    peak = max((w["plan"] or 0) for w in prog["year"])
    peak_month = next((dt.date.fromisoformat(w["monday"]).strftime("%B") for w in prog["year"] if (w["plan"] or 0) == peak and w.get("monday")), "the summer")
    now_plan = next((w["plan"] for w in prog["year"] if w.get("current")), prog["year"][0]["plan"])
    gap_min = round(prog["to_go_s"] / 60)
    updated = d(prog["updated"])
    results_out = today >= dt.date(2026, 12, 8)
    entry = [(n, g, t, ("Open" if results_out else "Opens Dec 8") if st == "TOUR" else st) for n, g, t, st in ENTRY]
    # my entry status comes from data/my-races.json (the races page reads the same line)
    mine = json.loads((ROOT / "data" / "my-races.json").read_text())["races"]
    chi = next((m for m in mine if "Chicago" in m["name"]), None)
    in_line = ("I'm in the drawing, and I find out December 8." if chi and "drawing" in chi["status"].lower() and not results_out
               else (chi["status"].rstrip(".") + "." if chi else ""))
    stops = [r for r in prog["races"] if r["date"] >= today.isoformat() and "Chicago" not in r["name"]]

    me = ' class="me"'
    std_rows = "".join(f'<tr{me if a == "40 to 44" else ""}><td>{a}</td><td>{m}</td><td>{w}</td></tr>' for a, m, w in STANDARDS)
    entry_rows = "".join(
        f'<div class="race{" final" if st == "Open" else ""}"><div class="d">{esc(st)}</div><h3>{esc(n)}</h3>'
        f'<div class="k">{esc(g)}</div><p class="rstatus">{esc(t)}</p></div>' for n, g, t, st in entry)
    stop_cards = "".join(
        f'<div class="race"><div class="d">{esc(nice(d(r["date"])))}</div><h3>{esc(r["name"])}</h3>'
        f'<div class="k">Watch says today</div><div class="v">{esc(r["today"])}</div></div>' for r in stops)
    faq_html = "".join(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in FAQ)

    LOTTERY = ("Lottery results went out <b>Tuesday, December 8, 2026</b>. If you weren't picked, charity entries stay open until September 10, 2027, and tour operators have entries too."
               if results_out else
               "Lottery results come out <b>Tuesday, December 8, 2026</b>. If you're not picked, charity entries stay open until September 10, 2027.")
    title = "Chicago Marathon 2027: Date, Lottery, Qualifying Times and a Sub-3 Training Plan | To The Finish"
    desc = ("The 2027 Chicago Marathon is Sunday, October 10. Lottery results, every way in, the 2027 qualifying "
            "times by age, and how I'm training to run it under 3 hours.")
    # no FAQPage markup: the AEO playbook rules it out (the rich result is gone); the answers stay on the page
    schema = {"@context": "https://schema.org", "@type": "WebPage", "name": "Chicago Marathon 2027 | To The Finish",
              "url": SITE + PATH, "description": desc, "dateModified": prog["updated"]}
    extra = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'

    form = """<form class="join" action="https://app.kit.com/forms/10209840/subscriptions" method="post" id="join-chicago" data-thanks="thanks-chicago">
      <input name="fields[first_name]" aria-label="First name" placeholder="First name" autocomplete="given-name">
      <input name="email_address" type="email" aria-label="Email" placeholder="Email" required autocomplete="email">
      <button type="submit">Get the Sunday letter</button>
    </form>
    <div class="thanks" id="thanks-chicago">You're in. There's a note from me in your inbox now, and the next letter comes Sunday night.</div>
    <p class="fine">The Sunday letter is what the week really was, with the new episode when there is one. One email a week. It's free, and you can unsubscribe anytime.</p>"""

    html = head(title, desc, PATH, extra) + f"""    <div class="page">
      <p class="kicker">Chicago Marathon 2027</p>
      <h1 class="display">Chicago <span class="o">2027.</span></h1>
      <p class="lead">Sunday, October 10, 2027, starting and finishing in Grant Park. Here's every way into the race, the 2027 qualifying times, and how I'm training to run it in under 3 hours.</p>
    </div>
  </div>
</header>
<section class="glance">
  <div class="wrap">
    <p class="kicker">The race</p>
    <div class="facts">
      <div><span class="k">Date</span><b>Sun Oct 10, 2027</b></div>
      <div><span class="k">Start and finish</span><b>Grant Park</b></div>
      <div><span class="k">Course</span><b>29 neighborhoods</b><span>The race calls it flat and fast</span></div>
      <div><span class="k">Time limit</span><b>6:30</b><span>A 15-minute mile</span></div>
      <div><span class="k">Entry</span><b>$250</b><span>US residents; $260 for everyone else</span></div>
      <div><span class="k">Expo</span><b>Oct 7 to 9</b><span>Thursday to Saturday</span></div>
    </div>
  </div>
</section>
<section>
  <div class="wrap">
    <p class="kicker">How to get in</p>
    <h2 class="display sec">Every way <span class="o">in.</span></h2>
    <p class="body">{LOTTERY}</p>
    <div class="rgrid entry">{entry_rows}</div>
  </div>
</section>
<section>
  <div class="wrap">
    <p class="kicker">Qualifying times</p>
    <h2 class="display sec">2027 time <span class="o">standards.</span></h2>
    <p class="body">These get you a guaranteed entry. They go by your age on race day, October 10, 2027. Non-binary standards match the women's.</p>
    <table class="ftable"><thead><tr><th scope="col">Age on race day</th><th scope="col">Men</th><th scope="col">Women</th></tr></thead><tbody>{std_rows}</tbody></table>
    <p class="note">The qualifying window for 2027 (Jan 1, 2025 to Oct 29, 2026) is closed.</p>
  </div>
</section>
<section class="mybuild">
  <div class="wrap">
    <p class="kicker">My sub-3 build</p>
    <h2 class="display sec">Under 3 hours, <span class="o">at 44.</span></h2>
    <p class="body">I'll be 44 on race day, and 3:00:00 is exactly Chicago's qualifying time for men 40 to 44. {esc(in_line)}</p>
    <div class="gapline"><div><span class="k">Watch says today</span><b>{esc(prog["now"]["marathon"])}</b></div><div class="arrow">to</div><div><span class="k">Goal</span><b class="o">{esc(prog["goal"])}</b></div></div>
    <p class="body">That's {gap_min} minutes to find in {weeks} weeks. The first number is what my Garmin thinks I'd run today. Kai, my AI running coach, has me at {now_plan} miles a week now and building to {peak} in {peak_month}, with hills at Mission Trails every week. Some weeks I'll be ahead of it. You'll see the other weeks too.</p>
    <div class="rgrid">{stop_cards}<div class="race final"><div class="d">{esc(nice(race_day))}</div><h3>Chicago Marathon</h3><div class="k">Goal</div><div class="v o">{esc(prog["goal"])}</div></div></div>
    <p class="note">Garmin prediction updated {updated:%b} {updated.day}, {updated.year}. <a href="/#progress">See the whole chart</a>, <a href="/races/">my race reports</a> or <a href="/san-diego-races/">the San Diego races I'm picking from</a>.</p>
  </div>
</section>
<section class="sunday" id="show">
  <div class="wrap">
    <p class="kicker">Running Chicago too?</p>
    <h2 class="display">See you in <span class="o">Grant Park.</span></h2>
    <p class="body">To The Finish is my show about chasing a sub-3 marathon at Chicago. Five AI coaches see what my watch records and what I tell them, and they argue over every run. If you're running it too, the Sunday letter is where I write down how my build is going, week by week.</p>
    {form}
  </div>
</section>
<section class="faq">
  <div class="wrap prose">
    <p class="kicker">Quick answers</p>
    {faq_html}
    <p class="note">Race facts from the Chicago Marathon's own pages (<a href="{SRC_APPLY}" rel="noopener">apply</a>, <a href="{SRC_COURSE}" rel="noopener">course</a>), checked {CHECKED}. This is my page, not the race's. Check their site before you sign up.</p>
  </div>
</section>
{FOOT}"""
    out = ROOT / "chicago-marathon-2027"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html)
    print(f"built chicago-marathon-2027 ({weeks} weeks out, plan {now_plan} -> {peak} mi)")


if __name__ == "__main__":
    main()
