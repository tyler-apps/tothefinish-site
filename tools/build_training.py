#!/usr/bin/env python3
"""Render the public journal from the allowlisted Brain export, never private sources."""
import datetime as dt
import json
from pathlib import Path
from build_pages import ROOT, FOOT, FORM, SITE, VER, esc, head, ld


def date(value, full=False):
    d=dt.date.fromisoformat(value)
    return f'{d:%B} {d.day}, {d.year}' if full else f'{d:%b} {d.day}'


def clock(value):
    if value is None: return 'Not recorded'
    s=round(value)
    return f'{s//3600}:{s%3600//60:02d}:{s%60:02d}' if s>=3600 else f'{s//60}:{s%60:02d}'


def num(value):
    return f'{value:g}' if isinstance(value,(int,float)) else 'Not recorded'


def week_chart(week):
    days=week['days']; peak=max([d['run_miles'] or 0 for d in days]+[1])
    items=[]
    for d in days:
        amount=d['run_miles']; state='Upcoming' if d['future'] else ('No run recorded' if amount is None or amount==0 else f'{amount:g} mi')
        height=max(3,round((amount or 0)/peak*100))
        items.append(f'<div class="week-day"><span class="week-value">{num(amount) if amount else "·"}</span><div class="week-track"><span style="height:{height}%" class="{"has-run" if amount else "empty-run"}"></span></div><b>{dt.date.fromisoformat(d["date"]):%a}</b><span class="sr-only">{esc(state)}</span></div>')
    return '<div class="training-week-chart" aria-label="Recorded running miles by day">'+''.join(items)+'</div>'


def effort_chart(session):
    efforts=[r for r in session.get('efforts',[]) if r['seconds']==45]
    if not efforts:return ''
    bars=[]
    for i,r in enumerate(efforts):
        x=45+i*74; h=r['meters']*1.1
        bars.append(f'<rect x="{x}" y="{210-h}" width="35" height="{h}" rx="3" fill="var(--orange)"/><text x="{x+17.5}" y="{198-h}" text-anchor="middle">{r["meters"]}</text><text class="chart-label" x="{x+17.5}" y="238" text-anchor="middle">{i+1}</text>')
    return ('<figure class="training-reps"><figcaption>Six uphill repeats<span>45 seconds each · distance in meters</span></figcaption><div class="plot">'
            '<svg viewBox="0 0 510 258" role="img" aria-label="Distance covered in each 45-second uphill repeat: '+', '.join(str(r['meters'])+' meters' for r in efforts)+'">'
            '<line x1="26" x2="494" y1="211" y2="211" stroke="var(--line)"/>'+''.join(bars)+'</svg></div>'
            '<p class="training-small">Repeat number across the bottom. The separate test climb follows these repeats; it is not included in this chart.</p></figure>')


def feature(session):
    if not session:return ''
    r=session['review']
    return f'''<section class="training-feature" aria-labelledby="training-feature-title"><div class="wrap">
    <div class="training-section-label"><p class="kicker">The coach’s notebook</p><span>{date(session['date'],True)}</span></div>
    <div class="training-feature-grid"><div><h2 class="display" id="training-feature-title">{esc(r['headline'])}</h2>
    <div class="training-coach"><img src="/assets/kai-96.webp" width="48" height="48" alt="Kai, my AI running coach" loading="lazy"><div><b>{esc(r['coach'])}</b><span>My summary of the recorded decision</span></div></div>
    <p class="training-decision">{esc(r['decision'])}</p><a class="more" href="#{session['key']}">Read the session</a></div>
    <div>{effort_chart(session)}<div class="training-next"><span class="training-label">The next check</span><p>{esc(r['next'])}</p></div></div></div></div></section>'''


def row(s):
    d=dt.date.fromisoformat(s['date'])
    metrics=(f'<span><b>{num(s["distance_mi"])}</b> mi</span><span><b>{clock(s["duration_s"])}</b> timer time</span><span><b>{num(s["ascent_ft"])}</b> ft climbed</span>' if s['kind']=='run' else f'<span><b>{len(s["movements"])}</b> movement{"s" if len(s["movements"])!=1 else ""} logged</span>')
    if s['kind']=='run':
        detail=f'<dl class="training-details-stats"><div><dt>Average heart rate</dt><dd>{num(s["avg_hr"])}{" bpm" if s["avg_hr"] is not None else ""}</dd></div><div><dt>Session peak</dt><dd>{num(s["peak_hr"])}{" bpm" if s["peak_hr"] is not None else ""}</dd></div></dl>'
    else:
        rows=''.join(f'<tr><th scope="row">{esc(m["name"])}</th><td>{num(m["load_lb"])}{" lb" if m["load_lb"] is not None else ""}</td><td>{m["sets"]} × {m["reps"]}</td></tr>' for m in s['movements'])
        detail='<div class="training-table-scroll"><table><caption>Reported sets only. Assumed sets are left out.</caption><thead><tr><th>Movement</th><th>Logged load</th><th>Sets × reps</th></tr></thead><tbody>'+rows+'</tbody></table></div>'
    review=s.get('review')
    if review:
        detail+='<div class="training-comparison">'+''.join(f'<div><h4>{label}</h4><p>{esc(review[key])}</p></div>' for key,label in [('planned','What was planned'),('observed','What happened'),('decision','The coach’s decision')])+'</div>'
    else:
        detail+='<p class="training-small">This entry shows recorded work. A reviewed coaching note has not been added.</p>'
    return f'''<article class="training-entry" data-kind="{s['kind']}" id="{s['key']}"><div class="training-date"><time datetime="{s['date']}"><span>{d:%b}</span><b>{d.day:02}</b><span>{d:%a}</span></time></div><div class="training-entry-body"><div class="training-entry-top"><p class="training-label">{'Run' if s['kind']=='run' else 'Strength'} · recorded</p><span>{esc(s['source'])}</span></div><h3>{esc(s['title'])}</h3><div class="training-entry-metrics">{metrics}</div><details><summary>Session details{' & coach’s note' if review else ''}</summary><div class="training-detail-content">{detail}</div></details></div></article>'''


def main():
    data=json.loads((ROOT/'data/training.json').read_text()); week=data['week']
    selected=next((s for s in data['sessions'] if s['key']==data['featured']),None)
    desc='My recorded runs and strength sessions on the way to a sub-three-hour marathon, with the real decisions from my AI coaches.'
    schema=ld({'@context':'https://schema.org','@type':'CollectionPage','name':'My training journal','url':SITE+'/training/','description':desc,'about':{'@type':'Person','name':'Tyler Stewart','url':SITE+'/#tyler'},'dateModified':data['as_of']})
    out=head('My training journal | To The Finish',desc,'/training/',schema+f'<link rel="stylesheet" href="/assets/training.css?v={VER}">')
    out+=f'''<div class="training-hero"><div><p class="kicker">The training journal</p><h1 class="display">The work.<br><span class="o">To Chicago.</span></h1><p class="training-intro">A dad chasing a sub-three-hour marathon. These are my recorded runs, the lifts I’ve logged, and the decisions behind the next session.</p><a class="more" href="#sessions">Explore the sessions</a></div><aside class="training-week"><div class="training-week-heading"><span class="training-label">This week</span><span>{date(week['start'])} to {date(week['end'])}</span></div><div class="training-week-total"><strong>{num(week['recorded_miles'])}</strong><span>miles recorded<br>of about {num(week['planned_miles'])} planned</span></div>{week_chart(week)}<p class="training-small">An empty column means no run is recorded or the day is ahead. It doesn’t mean a workout was missed.</p><div class="training-week-bottom"><span>{week['recorded_runs']} runs recorded</span><span>{week['recorded_strength']} strength sessions logged</span></div></aside></div><div class="training-freshness">Records checked {date(data['as_of'],True)} · latest session {date(data['latest_record'],True) if data['latest_record'] else 'not recorded'}</div></div></header>'''
    out+=feature(selected)
    out+=f'''<section class="training-log" id="sessions" aria-labelledby="training-log-title"><div class="wrap"><div class="section-intro"><div><p class="kicker">The last four weeks</p><h2 class="display" id="training-log-title">One session<br>at a time.</h2></div><p class="body">Runs come from my Garmin recordings. Strength entries come from the sets I’ve logged. A plan stays a plan until there’s a record of the work.</p></div><div class="training-log-toolbar"><div class="training-filters" role="group" aria-label="Filter recorded sessions" hidden><button type="button" data-filter="all" aria-pressed="true">All sessions</button><button type="button" data-filter="run" aria-pressed="false">Running</button><button type="button" data-filter="strength" aria-pressed="false">Strength</button></div><p id="training-count" role="status" aria-live="polite">{len(data['sessions'])} recorded sessions</p></div><div class="training-entries">{''.join(row(s) for s in data['sessions'])}</div><p id="training-empty" hidden>No sessions of this kind are recorded in this window.</p><p class="training-small training-log-note">{date(data['from_date'])} to {date(data['as_of'],True)}. No routes or private recovery records are shown. Unlogged work and assumed sets are not counted.</p></div></section>'''
    out+=f'''<section class="training-letter"><div class="wrap cols"><div><p class="kicker">The Sunday letter</p><h2 class="display">What the week<br>added up to.</h2><p class="body">The miles, the coaches’ calls and what went sideways. One letter on Sunday.</p></div><div>{FORM.format(id='training',button='Get the Sunday letter')}</div></div></section><script src="/assets/training.js?v={VER}" defer></script>'''+FOOT
    target=ROOT/'training'; target.mkdir(exist_ok=True); (target/'index.html').write_text(out)
    print(f'Built training journal: {len(data["sessions"])} recorded sessions')
    return data['as_of']


if __name__=='__main__':main()
