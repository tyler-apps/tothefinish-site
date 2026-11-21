/* episode-live.js: the homepage episode block switches to "out now" on its own (Tyler 2026-11-21: "Yes, automate it").
   The daily task adds each episode to /episodes/episodes.json (number, slug, title, date, youtube_id) the day it goes
   live; the newest one with a YouTube id and a date on or before today takes over the hero label and the episode block.
   Fallback when the file has none yet: Episode 1 airs Sun Nov 22, 9 AM PT, so after that it says "out now" and links
   to the channel. Before air nothing changes. */
(function () {
  function q(k) { return document.querySelector('[data-ep="' + k + '"]'); }
  function setText(k, t) { var n = q(k); if (n) n.textContent = t; }
  function live(ep) {
    var yt = ep.youtube_id && ep.youtube_id !== 'TBD' ? 'https://www.youtube.com/watch?v=' + ep.youtube_id
                                                      : 'https://www.youtube.com/@tothefinishai';
    var name = ep.title ? ' · ' + ep.title : '';
    setText('herok', 'Episode ' + ep.number + ' · Out now');
    setText('kicker', 'Episode ' + ep.number + name);
    if (ep.number === 1) {
      setText('when', 'now');
    } else {
      setText('body', 'Episode ' + ep.number + (ep.title ? ', ' + ep.title + ',' : '') +
        ' is out now on YouTube, Instagram, TikTok and X. A new one comes every Sunday, built from the week that really happened.');
    }
    var d = q('date'); if (d) d.innerHTML = 'Out<br>now';
    setText('where', 'Episode ' + ep.number + name);
    var bt = q('btn'); if (bt) { bt.href = yt; bt.textContent = 'Watch Episode ' + ep.number; }
  }
  function fallback() {
    if (Date.now() >= Date.parse('2026-11-22T09:00:00-08:00')) live({ number: 1, title: 'The Hiring' });
  }
  var today = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Los_Angeles' });
  fetch('/episodes/episodes.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (E) {
    var aired = (E || []).filter(function (e) { return e.youtube_id && e.youtube_id !== 'TBD' && e.date <= today; });
    if (aired.length) live(aired[aired.length - 1]); else fallback();
  }).catch(fallback);
})();
