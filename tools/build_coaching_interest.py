#!/usr/bin/env python3
"""Coaching interest, not access. Provider config is verified before release."""
import json
from build_pages import ROOT, FOOT, VER, SITE, esc, head, ld


def form(config):
    active = config['status'] == 'ready'
    action = f' action="https://app.kit.com/forms/{config["form_id"]}/subscriptions" method="post"' if active else ''
    disabled = '' if active else ' disabled'
    notice = '' if active else '<p class="interest-preview" role="status">Preview · Email signup is being connected. Nothing entered here is sent.</p>'
    return f'''{notice}<form class="join interest-form" id="coaching-interest" data-signup-purpose="coaching-interest"{action}>
    <fieldset{disabled}><legend class="visually-hidden">Coaching product updates</legend>
    <label for="interest-email">Email address<input id="interest-email" name="email_address" type="email" required autocomplete="email" maxlength="254" aria-describedby="interest-consent"></label>
    <label for="interest-challenge">What’s hardest to fit into your training?<span>Optional</span>
    <select id="interest-challenge" name="fields[{esc(config['challenge_field'])}]">
    <option value="">Choose one, or leave this blank</option>
    <option value="running_and_strength">Running and strength together</option>
    <option value="fueling">Eating around my training</option>
    <option value="recovery">Knowing when to push or recover</option>
    <option value="life_and_schedule">Making a plan fit my life</option>
    </select></label>
    <p class="interest-consent" id="interest-consent">Email me about the coaching product Tyler is exploring. Occasional updates when there’s something to report. Leave any time. This doesn’t add me to the Sunday letter.</p>
    <button type="submit">Get coaching updates <span aria-hidden="true">↗</span></button>
    </fieldset></form><p class="interest-footnote">{('Single opt-in. No confirmation email. Kit handles your signup. ' if active else '')}<a href="/privacy/">How I use your email</a> · No payment or watch connection.</p>'''


def main():
    config=json.loads((ROOT/'pages/coaching-interest.json').read_text())
    from check_coaching_interest import issues
    errors=issues(config)
    if errors:raise ValueError('; '.join(errors))
    desc='I’m exploring a coaching product that considers running, strength, food and recovery together. Get occasional updates, separate from my Sunday letter.'
    extra=f'<link rel="stylesheet" href="/assets/coaching-interest.css?v={VER}">'+ld({'@context':'https://schema.org','@type':'WebPage','name':'Coaching product updates','url':SITE+'/coaching/','description':desc})
    out=head('Coaching product updates | To The Finish',desc,'/coaching/',extra)
    out+='''<div class="interest-hero"><div><p class="kicker">The next chapter · In exploration</p>
    <h1 class="display">A team for<br>the <span class="o">whole week.</span></h1>
    <p class="interest-lead">I built five AI coaches to help me chase a sub-three-hour marathon. Now I’m exploring what it would take to put that kind of team around someone else’s training.</p>
    <a class="interest-jump" href="#updates">Get coaching updates <span aria-hidden="true">↓</span></a>
    <p class="interest-status">My personal setup is running. A public coaching product isn’t available yet.</p></div>
    <aside class="interest-board" aria-label="The idea behind my coaching team">
    <div class="interest-board-top"><span>The idea</span><span>One shared picture</span></div>
    <p class="interest-board-title">The run is only<br>part of the week.</p>
    <dl class="interest-inputs"><div><dt>What you did</dt><dd>Watch records and training history</dd></div><div><dt>What you can do</dt><dd>Your schedule and how you feel</dd></div><div><dt>What informs the call</dt><dd>Reviewed research and coaching rules</dd></div></dl>
    <div class="interest-staff" aria-label="My five AI coaches">'''
    for name,role in [('Kai','Running'),('Bo','Strength'),('Juno','Nutrition'),('Mo','Recovery'),('Rook','Head coach')]:
        out+=f'<div><img src="/assets/{name.lower()}-216.webp" width="72" height="72" alt="" loading="eager"><b>{name}</b><span>{role}</span></div>'
    out+='''</div><p class="interest-board-note">The AI characters from my own training setup.</p></aside></div></div></header>
    <section class="interest-context" aria-labelledby="interest-context-title"><div class="wrap interest-columns"><div><p class="kicker">What I want to carry forward</p><h2 class="display" id="interest-context-title">The decisions<br>between sessions.</h2></div><div class="interest-prose"><p>A hard run changes what I ask of my legs in the gym. The work I finish changes how I plan my food. My available time matters too.</p><p>That’s the idea I’m exploring for a product: coaches considering those trade-offs together, with a reason behind the next session.</p><a class="more" href="/#inside">See how my current setup works</a></div></div></section>
    <section class="interest-evidence" aria-labelledby="interest-evidence-title"><div class="wrap"><div class="interest-case"><div><p class="kicker">From my actual training · November 24, 2026</p><h2 class="display" id="interest-evidence-title">A hard effort.<br>A limit unchanged.</h2><p>I ran a test climb after my hill repeats. The session’s highest heart rate didn’t establish my true maximum, so my running coach kept the easy-run limit where it was.</p><a class="more" href="/training/">Read the recorded session</a></div><div class="interest-decision"><div><span>Recorded</span><strong>166 <small>bpm</small></strong><p>Session peak heart rate</p></div><div><span>Decision</span><strong>120 <small>bpm</small></strong><p>Easy-run limit retained</p></div><p class="interest-case-note">My own data and decision. This doesn’t establish a result for another runner.</p></div></div></div></section>
    <section id="updates" class="interest-signup" aria-labelledby="interest-signup-title"><div class="wrap interest-columns"><div><p class="kicker">Coaching product updates</p><h2 class="display" id="interest-signup-title">For your<br>own starting line.</h2><p class="interest-lead">If this is something you’d want for your training, I’d like to know.</p><p class="interest-status">I haven’t set a launch date or price. This is a way to hear what develops, with no promise of access.</p></div><div class="interest-form-panel">'''+form(config)+'''</div></div></section>
    <section class="interest-questions" aria-labelledby="interest-questions-title"><div class="wrap interest-columns"><div><p class="kicker">Before you leave your email</p><h2 class="display" id="interest-questions-title">Where it stands.</h2></div><div>
    <details><summary>What would I be signing up for?</summary><p>Occasional emails about the coaching product I’m exploring. No coaching service, payment or Garmin connection starts with this form.</p></details>
    <details><summary>Is this the Sunday letter?</summary><p>They’re separate choices. The Sunday letter is about my real training and the animated series. This list is for people who want to hear about the possible coaching product.</p></details>
    <details><summary>What is already real?</summary><p>My personal coaching setup uses my Garmin records, what I report and reviewed coaching rules. The training journal shows the work I’ve recorded and selected decisions. Making something other people can use is a separate step.</p></details>
    </div></div></section>'''+FOOT
    dest=ROOT/'coaching'; dest.mkdir(exist_ok=True); (dest/'index.html').write_text(out)
    print('Built coaching interest page: '+config['status'])
    return '2026-11-24'

if __name__=='__main__': main()
