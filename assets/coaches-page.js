/* coaches-page.js: fills /coaches/ from data/progress.json (built by the brain's scripts/site_progress.py) and
   draws every chart with assets/charts.js. Each chart leads with one takeaway, written from the data. */
(function () {
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  var DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  function day(d) { return new Date(d + 'T12:00:00'); }
  function md(d) { var x = day(d); return MON[x.getMonth()] + ' ' + x.getDate(); }
  function sec(t) { var p = t.split(':').map(Number); return p.length === 3 ? p[0] * 3600 + p[1] * 60 + p[2] : p[0] * 60 + p[1]; }
  function hm(s) { s = Math.round(s); return Math.floor(s / 3600) + ':' + String(Math.floor(s % 3600 / 60)).padStart(2, '0'); }
  function hms(s) { s = Math.round(s); return Math.floor(s / 3600) + ':' + String(Math.floor(s % 3600 / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0'); }
  function ms(s) { s = Math.round(s); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); }
  function set(k, v) { document.querySelectorAll('[data-k="' + k + '"]').forEach(function (n) { n.textContent = v; }); }
  function take(id, html) { var n = document.querySelector('[data-take="' + id + '"]'); if (n) n.innerHTML = html; }
  function $(id) { return document.getElementById(id); }
  /* Even calendar ticks: weekly or every other week under ~11 weeks, otherwise month starts every 1, 2, 3, 4, 6 or 12
     months (lined up on January) so the axis never skips unevenly. charts.js drops any label that would collide. */
  function monthTicks(xs) {
    var a = xs[0], b = xs[xs.length - 1], span = (b - a) / 864e5, out = [], d;
    if (span < 80) {
      var step = span < 40 ? 7 : 14;
      d = new Date(a.getFullYear(), a.getMonth(), a.getDate() + (8 - a.getDay()) % 7, 12);
      for (; d <= b; d = new Date(d.getFullYear(), d.getMonth(), d.getDate() + step, 12))
        if (d - a > 2 * 864e5 && b - d > 2 * 864e5) out.push({ x: d, label: MON[d.getMonth()] + ' ' + d.getDate() });
      return out;
    }
    var months = (b.getFullYear() - a.getFullYear()) * 12 + b.getMonth() - a.getMonth();
    var st = [1, 2, 3, 4, 6, 12].filter(function (n) { return months / n <= 5; })[0] || 12, long = span > 300;
    for (var k = 1; ; k++) {
      d = new Date(a.getFullYear(), a.getMonth() + k, 1, 12);
      if (d > b) break;
      if (d.getMonth() % st === 0) out.push({ x: d, label: MON[d.getMonth()] + (long ? ' \u2019' + String(d.getFullYear()).slice(2) : '') });
    }
    return out;
  }

  /* The coach bar under the header: the coach you're reading is lit, and on a phone the bar scrolls to keep it in view */
  var pills = document.querySelectorAll('.jump a');
  if ('IntersectionObserver' in window && pills.length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        pills.forEach(function (p) {
          var on = p.getAttribute('href') === '#' + e.target.id;
          if (on) { p.setAttribute('aria-current', 'true'); var bar = p.parentNode; bar.scrollTo({ left: p.offsetLeft - 16, behavior: 'smooth' }); }
          else p.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    document.querySelectorAll('section.cs, section.feed').forEach(function (sct) { io.observe(sct); });
  }


  fetch('/data/progress.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (D) {
    var T = window.TTF, today = new Date().toISOString().slice(0, 10);
    var CO = D.coaches || {};
    ['Rook', 'Kai', 'Mo', 'Bo', 'Juno'].forEach(function (c) {
      var x = CO[c]; if (!x) return; var k = c.toLowerCase();
      set('c_' + k + '_studies', x.studies); set('c_' + k + '_live', (x.live || 0).toLocaleString('en-US'));
    });
    if (CO.all_studies) set('c_all', CO.all_studies);
    var L = D.lines || {};
    document.querySelectorAll('[data-line]').forEach(function (e) {
      var t = L[e.getAttribute('data-line')]; if (t) e.textContent = t; else { var q = e.closest('.say'); if (q) q.remove(); }
    });

    /* Kai: threshold pace since 2024 (faster is up) */
    if (D.engine && D.engine.length && $('p-engine')) {
      var E = D.engine.map(function (p) { return { x: day(p.date), y: sec(p.pace) }; });
      var best = E.reduce(function (a, b) { return b.y < a.y ? b : a; });
      take('engine', '<b>' + ms(E[E.length - 1].y) + '</b> a mile now <span>' + ms(best.y) + ' at my best</span>');
      T.line($('p-engine'), { data: E, invert: true, yFmt: ms, yStep: 30, xTicks: monthTicks(E.map(function (p) { return p.x; })),
        marks: [{ x: best.x, y: best.y, label: ms(best.y) + ' best' }], endLabel: function (p) { return ms(p.y); },
        label: 'Threshold pace per mile, ' + ms(E[0].y) + ' in ' + MON[E[0].x.getMonth()] + ' ' + E[0].x.getFullYear() + ', best ' + ms(best.y) + ', now ' + ms(E[E.length - 1].y) });
    }

    /* Kai: meters per heartbeat */
    if (D.efficiency && D.efficiency.length > 1 && $('p-eff')) {
      var F = D.efficiency.map(function (p) { return { x: day(p.monday), y: p.mpb }; });
      var now = F[F.length - 1].y, then = F[Math.max(0, F.length - 5)].y, dlt = now - then;
      take('eff', '<b>' + now.toFixed(2) + '</b> meters a heartbeat <span>' + (dlt >= 0 ? '+' : '−') + Math.abs(dlt).toFixed(2) + ' in a month</span>');
      T.line($('p-eff'), { data: F, area: true, yFmt: function (v) { return v.toFixed(2); }, xTicks: monthTicks(F.map(function (p) { return p.x; })),
        endLabel: function (p) { return p.y.toFixed(2); }, label: 'Meters per heartbeat on easy runs, now ' + now.toFixed(2) });
    }

    /* Kai: weekly miles, planned vs run */
    if (D.year && $('p-miles')) {
      var W = (D.before || []).map(function (w) { return { monday: w.monday, done: w.done, plan: null }; })
        .concat(D.year.map(function (w) { return { monday: w.monday, done: w.done, plan: w.plan, current: w.current }; }));
      var seenM = {};
      var bars = W.map(function (w) {
        var x = day(w.monday), mk = x.getFullYear() * 12 + x.getMonth(), lab = '';
        if (!seenM[mk]) { seenM[mk] = 1; lab = MON[x.getMonth()]; }
        return { label: lab, v: w.done || 0, ghost: w.plan || 0, hot: !!w.current };
      });
      var cw = D.year.filter(function (w) { return w.current; })[0], peak = Math.max.apply(null, D.year.map(function (w) { return w.plan; }));
      take('miles', cw ? '<b>' + (cw.done || 0) + '</b> of ' + cw.plan + ' miles this week <span>' + peak + ' at the peak</span>' : peak + ' miles a week at the peak');
      T.bars($('p-miles'), { data: bars, thin: true, label: 'Weekly miles, planned and run; peak ' + peak });
    }

    /* Mo: easy share by week */
    if (D.mo && D.mo.easy && D.mo.easy.length && $('p-easy')) {
      var Ez = D.mo.easy, lastFull = Ez.filter(function (w) { return day(w.monday) <= new Date(Date.now() - 7 * 864e5); });
      var lw = lastFull.length ? lastFull[lastFull.length - 1] : Ez[Ez.length - 1];
      take('easy', '<b>' + lw.easy + '%</b> easy last week <span>the goal is 80%</span>');
      T.bars($('p-easy'), { data: Ez.map(function (w) { return { label: md(w.monday), v: w.easy, hot: w.easy >= 80 }; }),
        max: 100, goal: { v: 80, label: '80% goal' }, vFmt: function (v) { return v + '%'; }, label: 'Share of running time easy, by week' });
    }

    /* Mo: sleep */
    if (D.mo && D.mo.sleep && D.mo.sleep.length && $('p-sleep')) {
      var S = D.mo.sleep;
      take('sleep', '<b>' + D.mo.sleep_avg7.toFixed(1) + ' h</b> a night <span>' + D.mo.sleep_7plus + ' of ' + D.mo.sleep_worn7 + ' nights reached 7</span>');
      T.bars($('p-sleep'), { data: S.map(function (n) { var x = day(n.date); return { label: DOW[x.getDay()], v: n.hours || 0, hot: (n.hours || 0) >= 7, dim: n.broken }; }),
        max: 9, goal: { v: 7, label: '7 hours' }, vFmt: function (v) { return v.toFixed(1); }, label: 'Hours asleep each night' });
    }

    /* Bo: top sets */
    if (D.bo && D.bo.best && $('p-lifts')) {
      $('p-lifts').innerHTML = D.bo.best.map(function (b) {
        var from = b.first_lb && b.first_lb < b.lb ? 'Up from ' + b.first_lb + ' lb in ' + MON[day(b.first_date).getMonth()] : 'First tracked ' + md(b.first_date || b.date);
        return '<div class="lift"><p class="n">' + b.lift + ' · heaviest set</p><p class="v">' + b.lb + '<small>lb × ' + b.reps + '</small></p><p class="s">' + from + '</p></div>';
      }).join('');
    }

    /* Juno: carbs follow the work */
    if (D.juno && D.juno.week && D.juno.week.length && $('p-fuel')) {
      var J = D.juno.week, hi = J.reduce(function (a, b) { return b.carbs > a.carbs ? b : a; }), lo = J.reduce(function (a, b) { return b.carbs < a.carbs ? b : a; });
      var NAME = { long: 'long run', hard: 'hard run', easy: 'easy day', rest: 'rest day' };
      take('fuel', '<b>' + hi.carbs + ' g</b> for ' + DAYS[day(hi.date).getDay()] + '’s ' + (NAME[hi.work] || 'run') +
        ' <span>' + lo.carbs + ' g on ' + DAYS[day(lo.date).getDay()] + '’s ' + (NAME[lo.work] || 'day') + '</span>');
      T.bars($('p-fuel'), { data: J.map(function (x) { var dd = day(x.date); return { label: DOW[dd.getDay()], sub: (x.work || '').toUpperCase(), v: x.carbs, hot: x.work === 'hard' || x.work === 'long' }; }),
        subLabels: true, vFmt: function (v) { return v + 'g'; }, label: 'Grams of carbs a day, next seven days' });
    }

    /* Rook: the gap */
    if (D.gap && D.gap.length && $('p-gap')) {
      var G = D.gap.map(function (p) { return { x: day(p.date), y: sec(p.marathon) }; }), goal = sec('2:59:59');
      var found = G[0].y - G[G.length - 1].y;
      take('gap', '<b>' + hms(G[G.length - 1].y) + '</b> today <span>' + (found >= 0 ? ms(found) + ' found since ' + md(D.gap[0].date) : ms(-found) + ' slower than ' + md(D.gap[0].date)) + '</span>');
      T.line($('p-gap'), { data: G, invert: true, goal: { y: goal, label: 'Goal 2:59:59' }, yPad: 0.06, yFmt: hm, yStep: 1800,
        gapLabel: hm(G[G.length - 1].y - goal) + ' to find',
        xTicks: monthTicks(G.map(function (p) { return p.x; })), endLabel: function (p) { return hms(p.y); },
        label: 'Marathon prediction, ' + hms(G[0].y) + ' on ' + md(D.gap[0].date) + ', ' + hms(G[G.length - 1].y) + ' today, goal 2:59:59' });
    }

    /* Rook: who makes the calls */
    if (D.system && D.system.calls && $('p-calls')) {
      var Cl = D.system.calls, tot = 0, auto = 0;
      Cl.forEach(function (c) { tot += c.auto + c.called + c.yours; auto += c.auto; });
      take('calls', '<b>' + tot + '</b> calls since ' + md(D.system.calls_since) + ' <span>' + auto + ' automatic</span>');
      T.hbars($('p-calls'), { rows: Cl.map(function (c) { return { label: c.coach, parts: [{ v: c.auto, kind: 'auto' }, { v: c.called, kind: 'called' }, { v: c.yours, kind: 'yours' }] }; }),
        kinds: { auto: { fill: T.C.orange }, called: { fill: T.C.white }, yours: { fill: T.C.muted } }, label: 'Decisions by coach' });
    }
  }).catch(function () {});
})();
