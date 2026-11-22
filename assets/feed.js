/* feed.js: the raw data on /coaches/ (2026-11-22, Tyler: "let's really nerd out on all the data that my coaches see").
   Everything here is drawn from data/feed.json (built by the brain's scripts/site_feed.py from the watch files) with the
   chart kit in charts.js. Nothing is typed in: a number on screen is a number in the file. */
(function () {
  var T = window.TTF; if (!T || !T.kit) return;
  var K = T.kit, C = T.C, $ = function (id) { return document.getElementById(id); };
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  var RED = '#ff3b30';
  function day(d) { return new Date(d + 'T12:00:00'); }
  function md(d) { var x = day(d); return MON[x.getMonth()] + ' ' + x.getDate(); }
  function dmd(d) { return DOW[day(d).getDay()] + ' ' + md(d); }
  function ms(s) { s = Math.round(s); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); }
  function n(v, dec) { return v.toLocaleString('en-US', { minimumFractionDigits: dec || 0, maximumFractionDigits: dec || 0 }); }
  function take(id, html) { var e = document.querySelector('[data-take="' + id + '"]'); if (e) e.innerHTML = html; }
  function pct(a, p) { var s = a.slice().sort(function (x, y) { return x - y; }); return s[Math.min(s.length - 1, Math.max(0, Math.round(p * (s.length - 1))))]; }
  function path(pts) { var d = '', on = false; pts.forEach(function (p) { if (!p) { on = false; return; } d += (on ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); on = true; }); return d; }
  function ticks(a, b, small) {
    var out = [], months = (b.getFullYear() - a.getFullYear()) * 12 + b.getMonth() - a.getMonth(), d, k;
    if (months < 2) {
      for (d = new Date(a.getFullYear(), a.getMonth(), a.getDate() + (8 - a.getDay()) % 7, 12); d <= b; d = new Date(+d + 7 * 864e5)) out.push({ x: d, label: MON[d.getMonth()] + ' ' + d.getDate() });
      return out;
    }
    var st = [1, 2, 3, 4, 6, 12].filter(function (q) { return months / q <= (small ? 4 : 7); })[0] || 12, long = months > 10;
    for (k = 1; ; k++) { d = new Date(a.getFullYear(), a.getMonth() + k, 1, 12); if (d > b) break; if (d.getMonth() % st === 0) out.push({ x: d, label: MON[d.getMonth()] + (long ? ' ’' + String(d.getFullYear()).slice(2) : '') }); }
    return out;
  }

  /* ---- one run, every channel, one cursor ---------------------------------------------------------------------- */
  function fmtCh(c, v) { return v == null ? '–' : c.k === 'pace' ? ms(v) : n(v, c.dec || 0); }
  function run(R) {
    var host = $('p-run'), slider = $('run-at'); if (!host || !R) return;
    var N = R.channels[0].v.length, cur = Math.round(N * 0.22), draw = [];
    K.redraw(host, function () {
      var small = host.clientWidth < 520, lane = small ? 50 : 56, big = small ? 92 : 112, top = 6, B = 26;
      var L = small ? 8 : 128, Rr = small ? 8 : 96, H = top + big + (R.channels.length - 1) * lane + B;
      var g = K.svgFor(host, H), s = g.s, w = g.w, X = function (i) { return L + i / (N - 1) * (w - L - Rr); };
      var y = top; draw = [];
      (R.reps || []).forEach(function (r) {
        K.el(s, 'rect', { x: X(r[0] / R.span * (N - 1)), width: Math.max(2, X(r[1] / R.span * (N - 1)) - X(r[0] / R.span * (N - 1))), y: top, height: H - B - top, fill: C.white, opacity: 0.13 });
      });
      R.channels.forEach(function (c, ci) {
        var h = ci ? lane : big, v = c.v.filter(function (q) { return q != null; }), lo = pct(v, 0.01), hi = pct(v, 0.99);
        if (c.k === 'pace') hi = Math.min(hi, 1200);
        if (c.k === 'hr' && R.cap) hi = Math.max(hi, R.cap + 4);
        var y0 = y + (small ? 20 : 8), y1 = y + h - 8, inv = c.k === 'pace';
        var Y = function (q) { var f = (Math.max(lo, Math.min(hi, q)) - lo) / ((hi - lo) || 1); if (inv) f = 1 - f; return y1 - f * (y1 - y0); };
        K.el(s, 'line', { x1: small ? 8 : 0, x2: w, y1: y + h, y2: y + h, stroke: C.grid });
        var pts = c.v.map(function (q, i) { return q == null ? null : [X(i), Y(q)]; });
        if (c.k === 'alt') {
          var good = pts.filter(Boolean);
          K.el(s, 'path', { d: path(good) + 'L' + good[good.length - 1][0] + ' ' + y1 + 'L' + good[0][0] + ' ' + y1 + 'Z', fill: C.orange, opacity: 0.16 });
        }
        if (c.k === 'hr' && R.cap) {
          K.el(s, 'line', { x1: L, x2: w - Rr, y1: Y(R.cap), y2: Y(R.cap), stroke: C.white, 'stroke-width': 1, 'stroke-dasharray': '4 5', opacity: 0.7 });
          if (!small) K.text(s, w - Rr, Y(R.cap) - 5, 'easy days stay under ' + R.cap, { anchor: 'end', fill: C.white, size: 12, weight: 600 });
        }
        K.el(s, 'path', { d: path(pts), fill: 'none', stroke: ci ? C.soft : C.orange, 'stroke-width': ci ? 1.4 : 2.2, 'stroke-linejoin': 'round' });
        if (c.k === 'hr' && R.cap) K.el(s, 'path', { d: path(c.v.map(function (q, i) { return q != null && q > R.cap ? [X(i), Y(q)] : null; })), fill: 'none', stroke: RED, 'stroke-width': 4, 'stroke-linecap': 'round' });
        K.text(s, small ? 8 : 0, small ? y + 14 : y + h / 2 + (ci ? 0 : -6), c.label + (small && !ci && R.cap ? ', easy under ' + R.cap : ''), { fill: C.axis, size: 13, weight: 600 });
        var val = K.text(s, w, small ? y + 15 : y + h / 2 + (ci ? 6 : 8), '', { anchor: 'end', fill: ci ? C.white : C.orange, weight: 800, size: ci ? (small ? 18 : 21) : (small ? 24 : 32), display: true });
        if (!small) K.text(s, 0, y + h / 2 + (ci ? 16 : 10), c.unit, { size: 12, fill: '#7a736c' });
        var dot = K.el(s, 'circle', { r: ci ? 3.5 : 5, fill: ci ? C.white : C.orange, stroke: C.ink, 'stroke-width': 1.5 });
        draw.push({ c: c, Y: Y, val: val, dot: dot, small: small });
        y += h;
      });
      var bar = K.el(s, 'line', { y1: top, y2: H - B, stroke: C.white, 'stroke-width': 1, opacity: 0.55 });
      var lab = K.text(s, 0, H - 8, '', { anchor: 'middle', fill: C.white, size: 13, weight: 700 });
      function put(i) {
        cur = Math.max(0, Math.min(N - 1, i));
        var x = X(cur); bar.setAttribute('x1', x); bar.setAttribute('x2', x);
        lab.textContent = ms(cur / (N - 1) * R.span); lab.setAttribute('x', Math.max(18, Math.min(w - 18, x)));
        draw.forEach(function (d) {
          var v = d.c.v[cur];
          d.val.textContent = fmtCh(d.c, v) + (d.small && d.c.unit !== 'min/mi' ? ' ' + d.c.unit : '');
          if (d.c.k === 'hr') d.val.setAttribute('fill', R.cap && v > R.cap ? RED : C.orange);
          if (v == null) d.dot.setAttribute('opacity', 0); else { d.dot.setAttribute('opacity', 1); d.dot.setAttribute('cx', x); d.dot.setAttribute('cy', d.Y(v)); }
        });
        if (slider && +slider.value !== cur) slider.value = cur;
      }
      function at(e) { var b = s.getBoundingClientRect(); put(Math.round((e.clientX - b.left - L) / (w - L - Rr) * (N - 1))); }
      s.style.touchAction = 'pan-y'; s.style.cursor = 'ew-resize';
      s.addEventListener('pointermove', at); s.addEventListener('pointerdown', at);
      host._put = put; put(cur);
    });
    if (slider) { slider.max = N - 1; slider.addEventListener('input', function () { host._put(+slider.value); }); slider.value = cur; }
    host.setAttribute('aria-label', 'Every sensor over one run on ' + dmd(R.date) + ': ' + R.channels.map(function (c) { return c.label; }).join(', '));
    take('run', '<b>' + n(R.readings) + '</b> readings in ' + R.miles.toFixed(1) + ' miles <span>' + dmd(R.date) + ', ' + R.channels.length + ' sensor lines</span>');
  }

  /* ---- one minute of heartbeats --------------------------------------------------------------------------------- */
  function beats(b) {
    var host = $('p-beats'); if (!host || !b) return;
    K.redraw(host, function () {
      var g = K.svgFor(host, 200), s = g.s, w = g.w, h = g.h, L = 40, B = 26, T0 = 12, v = b.ms;
      var lo = Math.min.apply(null, v) - 12, hi = Math.max.apply(null, v) + 6, t = 0, tot = v.reduce(function (a, q) { return a + q; }, 0);
      K.niceTicks(lo, hi, 3).forEach(function (q) { var yy = T0 + (1 - (q - lo) / (hi - lo)) * (h - B - T0); K.el(s, 'line', { x1: L, x2: w, y1: yy, y2: yy, stroke: C.grid }); K.text(s, L - 6, yy + 4, q, { anchor: 'end' }); });
      var pts = v.map(function (q) { var p = [L + t / tot * (w - L - 4), T0 + (1 - (q - lo) / (hi - lo)) * (h - B - T0)]; t += q; return p; });
      K.el(s, 'path', { d: path(pts), fill: 'none', stroke: C.orange, 'stroke-width': 1.2, opacity: 0.55 });
      pts.forEach(function (p) { K.el(s, 'circle', { cx: p[0], cy: p[1], r: w < 520 ? 2 : 3, fill: C.orange }); });
      K.text(s, L, h - 6, '0 s'); K.text(s, w, h - 6, '60 s', { anchor: 'end' });
    });
    var a = Math.min.apply(null, b.ms), z = Math.max.apply(null, b.ms);
    take('beats', '<b>' + b.ms.length + '</b> beats in one minute <span>' + a + ' to ' + z + ' ms apart</span>');
    host.setAttribute('aria-label', b.ms.length + ' heartbeats in one minute, ' + a + ' to ' + z + ' milliseconds apart');
  }

  /* ---- every run ------------------------------------------------------------------------------------------------- */
  function mix(f) { var a = [95, 87, 80], b = [255, 106, 31]; return 'rgb(' + a.map(function (q, i) { return Math.round(q + (b[i] - q) * f); }).join(',') + ')'; }
  function all(D, tot) {
    var host = $('p-all'), tip = $('tip-all'); if (!host || !D) return;
    K.redraw(host, function () {
      var small = host.clientWidth < 520, g = K.svgFor(host, small ? 280 : 360), s = g.s, w = g.w, h = g.h, L = 44, Rr = 10, T0 = 12, B = 28;
      var x0 = +day(D[0][0]), x1 = +day(D[D.length - 1][0]), lo = 360, hi = 960;
      var X = function (d) { return L + (+day(d) - x0) / (x1 - x0) * (w - L - Rr); }, Y = function (p) { return T0 + (Math.min(hi, Math.max(lo, p)) - lo) / (hi - lo) * (h - T0 - B); };
      [360, 480, 600, 720, 840].forEach(function (p) { K.el(s, 'line', { x1: L, x2: w - Rr, y1: Y(p), y2: Y(p), stroke: C.grid }); K.text(s, L - 8, Y(p) + 4, ms(p), { anchor: 'end' }); });
      K.xLabels(s, ticks(new Date(x0), new Date(x1), small).map(function (t) { return { x: X(t.x.toISOString().slice(0, 10)), label: t.label }; }), h - 8, L, w - Rr);
      var P = D.map(function (r) { return { r: r, x: X(r[0]), y: Y(r[2]) }; });
      P.forEach(function (p) { K.el(s, 'circle', { cx: p.x, cy: p.y, r: Math.max(2, Math.sqrt(p.r[1]) * (small ? 1.2 : 1.7)), fill: mix(Math.max(0, Math.min(1, (p.r[3] - 100) / 60))), opacity: 0.78 }); });
      var ring = K.el(s, 'circle', { r: 9, fill: 'none', stroke: C.white, 'stroke-width': 2, opacity: 0 });
      function near(e) {
        var b = s.getBoundingClientRect(), mx = e.clientX - b.left, my = e.clientY - b.top, best, bd = 900;
        P.forEach(function (p) { var d = (p.x - mx) * (p.x - mx) + (p.y - my) * (p.y - my); if (d < bd) { bd = d; best = p; } });
        if (!best) return;
        ring.setAttribute('cx', best.x); ring.setAttribute('cy', best.y); ring.setAttribute('opacity', 1);
        tip.textContent = dmd(best.r[0]) + ', ' + best.r[0].slice(0, 4) + ': ' + best.r[1].toFixed(1) + ' miles at ' + ms(best.r[2]) + ', heart rate ' + best.r[3];
      }
      s.addEventListener('pointermove', near); s.addEventListener('pointerdown', near); s.style.touchAction = 'pan-y';
    });
    take('all', '<b>' + n(tot.runs) + '</b> runs, <b>' + n(tot.miles) + '</b> miles <span>one dot a run</span>');
    host.setAttribute('aria-label', D.length + ' runs since ' + md(D[0][0]) + ' ' + D[0][0].slice(0, 4) + ', by date and pace');
  }

  /* ---- stacked bars, band, plain series --------------------------------------------------------------------------- */
  function stack(id, rows, fills, label) {
    var host = $('p-' + id); if (!host || !rows.length) return;
    K.redraw(host, function () {
      var small = host.clientWidth < 520, g = K.svgFor(host, small ? 220 : 250), s = g.s, w = g.w, h = g.h, L = 34, B = 24, T0 = 10, N = rows.length, bw = (w - L) / N;
      var mx = Math.max.apply(null, rows.map(function (r) { return r.parts.reduce(function (a, q) { return a + (q || 0); }, 0); })) * 1.04;
      K.niceTicks(0, mx, 3).forEach(function (q) { var yy = T0 + (1 - q / mx) * (h - T0 - B); K.el(s, 'line', { x1: L, x2: w, y1: yy, y2: yy, stroke: C.grid }); K.text(s, L - 6, yy + 4, q, { anchor: 'end' }); });
      var xs = [];
      rows.forEach(function (r, i) {
        var yy = h - B;
        r.parts.forEach(function (q, k) { if (!q) return; var hh = q / mx * (h - T0 - B); yy -= hh; K.el(s, 'rect', { x: L + i * bw + bw * 0.12, width: bw * 0.76, y: yy, height: Math.max(0.6, hh - 0.8), fill: fills[k] }); });
        xs.push({ x: L + (i + 0.5) * bw, label: md(r.d) });
      });
      var every = Math.ceil(N / (small ? 4 : 7));
      K.xLabels(s, xs.filter(function (q, i) { return (N - 1 - i) % every === 0; }), h - 6, L, w);
    });
    host.setAttribute('aria-label', label);
  }
  function series(id, rows, o) {
    var host = $('p-' + id); if (!host || !rows || rows.length < 2) return; o = o || {};
    K.redraw(host, function () {
      var small = host.clientWidth < 520, g = K.svgFor(host, o.h || (small ? 210 : 240)), s = g.s, w = g.w, h = g.h, L = 40, Rr = o.end === false ? 8 : 56, T0 = 12, B = 26;
      var ys = []; rows.forEach(function (r) { ys.push(r.v); if (o.band && r.lo) ys.push(r.lo, r.hi); if (r.cap) ys.push(r.cap); });
      var lo = Math.min.apply(null, ys), hi = Math.max.apply(null, ys), pad = (hi - lo) * 0.1 || 1; lo -= pad; hi += pad; if (o.zero) lo = 0;
      var x0 = +day(rows[0].date), x1 = +day(rows[rows.length - 1].date);
      var X = function (d) { return L + (+day(d) - x0) / ((x1 - x0) || 1) * (w - L - Rr); }, Y = function (v) { return T0 + (1 - (v - lo) / (hi - lo)) * (h - T0 - B); };
      K.niceTicks(lo, hi, 3).forEach(function (q) { K.el(s, 'line', { x1: L, x2: w - Rr, y1: Y(q), y2: Y(q), stroke: C.grid }); K.text(s, L - 6, Y(q) + 4, q, { anchor: 'end' }); });
      K.xLabels(s, ticks(new Date(x0), new Date(x1), small).map(function (t) { return { x: X(t.x.toISOString().slice(0, 10)), label: t.label }; }), h - 6, L, w - Rr);
      var day1 = (w - L - Rr) / ((x1 - x0) / 864e5);
      if (o.band) rows.forEach(function (r) { if (r.lo) K.el(s, 'rect', { x: X(r.date) - Math.max(2, day1 / 2), width: Math.max(4, day1 + 0.5), y: Y(r.hi), height: Y(r.lo) - Y(r.hi), fill: C.muted, opacity: 0.38 }); });
      if (o.bars) {
        var bw = Math.max(2, (w - L - Rr) / rows.length * 0.6);
        rows.forEach(function (r) { K.el(s, 'rect', { x: X(r.date) - bw / 2, width: bw, y: Y(r.v), height: h - B - Y(r.v), fill: r.v > (r.cap || 1e9) ? RED : C.orange, rx: 1.5 }); });
        K.el(s, 'path', { d: path(rows.map(function (r) { return r.cap ? [X(r.date), Y(r.cap)] : null; })), fill: 'none', stroke: C.white, 'stroke-width': 1.6, 'stroke-dasharray': '5 5' });
      } else {
        var pts = []; rows.forEach(function (r, i) { if (i && day(r.date) - day(rows[i - 1].date) > (o.gap || 4) * 864e5) pts.push(null); pts.push([X(r.date), Y(r.v)]); });
        K.el(s, 'path', { d: path(pts), fill: 'none', stroke: C.orange, 'stroke-width': rows.length > 90 ? 1.6 : 2.2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' });
        if (rows.length < 60) rows.forEach(function (r) { K.el(s, 'circle', { cx: X(r.date), cy: Y(r.v), r: 3, fill: C.orange }); });
      }
      var e = rows[rows.length - 1];
      if (o.end !== false && !o.bars) { K.el(s, 'circle', { cx: X(e.date), cy: Y(e.v), r: 5.5, fill: C.orange, stroke: C.ink, 'stroke-width': 2 }); K.text(s, X(e.date) + 10, Y(e.v) + 6, n(e.v, o.dec || 0), { fill: C.white, weight: 800, size: 19, display: true }); }
    });
    host.setAttribute('aria-label', o.label || '');
  }

  /* the number grids: first 12, then a button */
  document.querySelectorAll('.nums').forEach(function (g) {
    var btn = g.parentNode.querySelector('.allnums'); if (!btn) return;
    g.classList.add('short'); btn.hidden = false;
    btn.addEventListener('click', function () { var open = g.classList.toggle('short'); btn.setAttribute('aria-expanded', String(!open)); btn.textContent = open ? btn.dataset.more : btn.dataset.less; });
  });

  fetch('/data/feed.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (D) {
    var Ch = D.charts, last = function (a) { return a[a.length - 1]; };
    run(D.run); beats(D.beats); all(D.all, D.totals);
    var z = Ch.zones; if (z.length) {
      var wk = last(z), tot = wk.z.reduce(function (a, q) { return a + q; }, 0);
      take('zones', '<b>' + n(tot) + '</b> minutes in the zones this week <span>' + n(wk.z[3] + wk.z[4]) + ' of them hard</span>');
      stack('zones', z.map(function (r) { return { d: r.monday, parts: r.z }; }), ['#4d463f', '#7a7068', '#c48a63', C.orange, C.white], 'Minutes in each heart rate zone by week');
    }
    var F = { gct: ['ms on the ground', 0], cadence: ['steps a minute', 0], step: ['inches a step', 1], vr: ['% bounce per step', 1] }, bits = [];
    Ch.form.forEach(function (f) {
      var rows = f.rows.map(function (r) { return { date: r.monday, v: r.v }; }); if (rows.length < 2) return;
      var h = $('h-form-' + f.k); if (h) h.innerHTML = '<b>' + n(last(rows).v, F[f.k][1]) + '</b> ' + F[f.k][0];
      series('form-' + f.k, rows, { h: 150, end: false, gap: 22, label: F[f.k][0] + ' by week' });
    });
    take('form', 'Four ways to look at <b>one step</b>');
    if (Ch.hrv.length) { var q = last(Ch.hrv); take('hrv', '<b>' + q.v + ' ms</b> last night <span>my normal is ' + q.lo + ' to ' + q.hi + '</span>'); series('hrv', Ch.hrv, { band: true, label: 'Overnight heart rate variability, ' + q.v + ' ms on ' + md(q.date) }); }
    if (Ch.rhr.length) { var r0 = Math.max.apply(null, Ch.rhr.map(function (q) { return q.v; })); take('rhr', '<b>' + n(last(Ch.rhr).v) + '</b> beats a minute at rest <span>' + n(r0) + ' at the highest this year</span>'); series('rhr', Ch.rhr, { label: 'Resting heart rate each day' }); }
    if (Ch.load.length) { var mx = Math.max.apply(null, Ch.load.map(function (q) { return q.v; })); take('load', '<b>' + n(last(Ch.load).v) + '</b> over the last seven days <span>' + n(mx) + ' at the most since ' + md(Ch.load[0].date) + '</span>'); series('load', Ch.load, { zero: true, label: 'Seven day training load' }); }
    if (Ch.stages.length) { var st = last(Ch.stages); take('stages', '<b>' + st.deep.toFixed(1) + ' h</b> deep, <b>' + st.rem.toFixed(1) + ' h</b> REM <span>the night before ' + dmd(st.date) + '</span>');
      stack('stages', Ch.stages.map(function (q) { return { d: q.date, parts: [q.deep, q.rem, q.light, q.awake] }; }), [C.orange, C.white, C.muted, '#4d463f'], 'Hours in each stage of sleep'); }
    if (Ch.spike.length) { var sp = last(Ch.spike); take('spike', '<b>' + n(sp.minutes) + '</b> minutes on ' + dmd(sp.date) + ' <span>the ceiling was ' + n(sp.cap) + '</span>'); series('spike', Ch.spike.map(function (q) { return { date: q.date, v: q.minutes, cap: q.cap }; }), { bars: true, zero: true, end: false, label: 'Minutes of each run against the ceiling' }); }
  }).catch(function () {});
})();
