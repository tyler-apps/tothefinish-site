/* charts.js: the To The Finish chart system (2026-11-21, Tyler: "redesign the charts for a coaches page").
   One look for every chart: drawn at the real pixel width (redrawn on resize, so text never scales), 2-3 faint
   gridlines, direct labels instead of legends, orange only for "now", white dashed lines for goals, muted history.
   Usage: TTF.line(el, opts) · TTF.bars(el, opts) · TTF.hbars(el, opts). Each returns nothing; it owns el's content. */
(function () {
  var NS = 'http://www.w3.org/2000/svg';
  var C = { orange: '#ff6a1f', white: '#ffffff', ink: '#12100e', grid: '#2f2a25', axis: '#8a837c', muted: '#5f5750',
            soft: '#e7e1db', faint: '#3a342e' };
  var FONT = '-apple-system,BlinkMacSystemFont,"Inter","Segoe UI",Helvetica,Arial,sans-serif';
  var DISPLAY = '"Barlow Condensed",Impact,sans-serif';

  function el(parent, tag, attrs, text) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (text != null) n.textContent = text;
    parent.appendChild(n);
    return n;
  }
  function svgFor(host, h) {
    host.innerHTML = '';
    var w = Math.max(280, host.clientWidth);
    var s = el(host, 'svg', { width: w, height: h, viewBox: '0 0 ' + w + ' ' + h, 'font-family': FONT });
    s.style.display = 'block';
    s.style.overflow = 'visible';
    return { s: s, w: w, h: h, small: w < 520 };
  }
  function text(s, x, y, str, o) {
    o = o || {};
    return el(s, 'text', { x: x, y: y, fill: o.fill || C.axis, 'font-size': o.size || 12, 'font-weight': o.weight || 500,
      'text-anchor': o.anchor || 'start', 'font-family': o.display ? DISPLAY : FONT,
      'letter-spacing': o.display ? 0.5 : 0 }, str);
  }
  function niceTicks(lo, hi, n) {
    var span = hi - lo || 1, step = Math.pow(10, Math.floor(Math.log10(span / n)));
    [1, 2, 2.5, 5, 10].some(function (m) { if (span / (step * m) <= n + 0.5) { step *= m; return true; } return false; });
    function make(st) { var out = [], t = Math.ceil(lo / st) * st; for (; t <= hi + 1e-9; t += st) out.push(+t.toFixed(6)); return out; }
    var out = make(step);
    if (out.length < 2) out = make(step / 2);
    return out;
  }
  /* x-axis labels, dropped when one would touch the last one drawn or run past the plot */
  function xLabels(s, ticks, y, lo, hi) {
    var last = -1e9;
    ticks.forEach(function (t) {
      var half = t.label.length * 3.4 + 2;
      if (t.x - half < last + 10 || t.x - half < lo - 20 || t.x + half > hi + 20) return;
      text(s, t.x, y, t.label, { anchor: 'middle' }); last = t.x + half;
    });
  }
  function redraw(host, fn) {
    fn();
    if (window.ResizeObserver) {
      var last = host.clientWidth;
      new ResizeObserver(function () { if (Math.abs(host.clientWidth - last) > 4) { last = host.clientWidth; fn(); } }).observe(host);
    }
  }

  /* line: x = Date or number, y = number. opts: data [{x,y}], h, yFmt, xFmt, goal {y,label}, invert (smaller is
     better, so up = good), extend [{x,y}] dashed projection, area (fill under), endLabel fmt, yPad,
     gapLabel (with goal: shades the space between the line and the goal and names it) */
  function line(host, o) {
    redraw(host, function () {
      var g = svgFor(host, o.h || (host.clientWidth < 520 ? 220 : 260)), s = g.s, w = g.w, h = g.h;
      var pts = o.data, all = pts.concat(o.extend || []);
      var ys = all.map(function (p) { return p.y; }); if (o.goal) ys.push(o.goal.y);
      var lo = Math.min.apply(null, ys), hi = Math.max.apply(null, ys), pad = (hi - lo) * (o.yPad || 0.12) || 1;
      lo -= pad; hi += pad;
      var xs = all.map(function (p) { return +p.x; }), x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs);
      var L = g.small ? 44 : 52, R = g.small ? 52 : 64, T = 14, B = 28;
      function X(v) { return L + (+v - x0) / ((x1 - x0) || 1) * (w - L - R); }
      function Y(v) { var f = (v - lo) / ((hi - lo) || 1); if (o.invert) f = 1 - f; return T + (1 - f) * (h - T - B); }
      var ticks = o.yStep ? (function () { var a = [], t = Math.ceil(lo / o.yStep) * o.yStep; for (; t <= hi; t += o.yStep) a.push(t); return a; })() : niceTicks(lo, hi, 3);
      ticks.forEach(function (t) {
        el(s, 'line', { x1: L, x2: w - R, y1: Y(t), y2: Y(t), stroke: C.grid, 'stroke-width': 1 });
        text(s, L - 8, Y(t) + 4, o.yFmt ? o.yFmt(t) : t, { anchor: 'end' });
      });
      xLabels(s, (o.xTicks || []).map(function (t) { return { x: X(t.x), label: t.label }; }), h - 8, L, w - R);
      if (o.goal) {
        el(s, 'line', { x1: L, x2: w - R, y1: Y(o.goal.y), y2: Y(o.goal.y), stroke: C.white, 'stroke-width': 1.5, 'stroke-dasharray': '6 6', opacity: 0.85 });
        text(s, w - R, Y(o.goal.y) - 8, o.goal.label, { anchor: 'end', fill: C.white, weight: 700, size: 12 });
      }
      if (o.goal && o.gapLabel) {   /* the distance still to cover: shaded between the line and the goal, named once */
        var gp = pts.map(function (p, i) { return (i ? 'L' : 'M') + X(p.x).toFixed(1) + ' ' + Y(p.y).toFixed(1); }).join(' ');
        el(s, 'path', { d: gp + ' L' + X(pts[pts.length - 1].x).toFixed(1) + ' ' + Y(o.goal.y).toFixed(1) + ' L' + X(pts[0].x).toFixed(1) + ' ' + Y(o.goal.y).toFixed(1) + ' Z', fill: C.orange, opacity: 0.09 });
        var mid = pts[Math.floor(pts.length / 2)];
        text(s, X(mid.x), (Y(mid.y) + Y(o.goal.y)) / 2 + 6, o.gapLabel, { anchor: 'middle', fill: C.orange, weight: 800, size: g.small ? 20 : 24, display: true });
      }
      var d = pts.map(function (p, i) { return (i ? 'L' : 'M') + X(p.x).toFixed(1) + ' ' + Y(p.y).toFixed(1); }).join(' ');
      if (o.area) {
        var base = o.invert ? T : h - B;
        el(s, 'path', { d: d + ' L' + X(pts[pts.length - 1].x).toFixed(1) + ' ' + base + ' L' + X(pts[0].x).toFixed(1) + ' ' + base + ' Z', fill: C.orange, opacity: 0.08 });
      }
      if (o.extend && o.extend.length) {
        var e = [pts[pts.length - 1]].concat(o.extend);
        el(s, 'path', { d: e.map(function (p, i) { return (i ? 'L' : 'M') + X(p.x).toFixed(1) + ' ' + Y(p.y).toFixed(1); }).join(' '),
          fill: 'none', stroke: C.orange, 'stroke-width': 1.5, 'stroke-dasharray': '2 6', 'stroke-linecap': 'round', opacity: 0.7 });
        if (o.extendLabel) { var m = e[Math.floor(e.length / 2)]; text(s, (X(e[0].x) + X(e[e.length - 1].x)) / 2, (Y(e[0].y) + Y(e[e.length - 1].y)) / 2 - 10, o.extendLabel, { anchor: 'middle', size: 12 }); }
      }
      el(s, 'path', { d: d, fill: 'none', stroke: C.orange, 'stroke-width': 2.5, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' });
      (o.marks || []).forEach(function (m) {
        el(s, 'circle', { cx: X(m.x), cy: Y(m.y), r: 4, fill: C.ink, stroke: C.soft, 'stroke-width': 2 });
        text(s, X(m.x), Y(m.y) + (m.below ? 20 : -12), m.label, { anchor: 'middle', fill: C.soft, size: 12, weight: 600 });
      });
      var last = pts[pts.length - 1];
      el(s, 'circle', { cx: X(last.x), cy: Y(last.y), r: 5.5, fill: C.orange, stroke: C.ink, 'stroke-width': 2 });
      if (o.endLabel) text(s, X(last.x) + 10, Y(last.y) + 5, o.endLabel(last), { fill: C.white, weight: 800, size: g.small ? 16 : 18, display: true });
      host.setAttribute('aria-label', o.label || '');
    });
  }

  /* bars: vertical. opts: data [{label, v, hot (orange), ghost (outline, planned), sub, note}], goal {v,label},
     h, vFmt, max, showValues (true), thin (many bars: no value labels, sparse x labels) */
  function bars(host, o) {
    redraw(host, function () {
      var g = svgFor(host, o.h || (host.clientWidth < 520 ? 220 : 260)), s = g.s, w = g.w, h = g.h, D = o.data;
      var mx = o.max || Math.max.apply(null, D.map(function (d) { return Math.max(d.v || 0, d.ghost || 0); }).concat(o.goal ? [o.goal.v] : []));
      mx *= 1.16;
      var L = 8, R = 8, T = 18, B = o.subLabels ? 40 : 24, n = D.length, bw = (w - L - R) / n, gap = Math.min(10, bw * (o.thin ? 0.25 : 0.28));
      function Y(v) { return T + (1 - v / mx) * (h - T - B); }
      el(s, 'line', { x1: L, x2: w - R, y1: h - B, y2: h - B, stroke: C.grid });
      if (o.goal) {
        el(s, 'line', { x1: L, x2: w - R, y1: Y(o.goal.v), y2: Y(o.goal.v), stroke: C.white, 'stroke-width': 1.5, 'stroke-dasharray': '6 6', opacity: 0.85 });
        text(s, w - R, Y(o.goal.v) - 7, o.goal.label, { anchor: 'end', fill: C.white, weight: 700 });
      }
      var lastLab = -999;
      D.forEach(function (d, i) {
        var x = L + i * bw + gap / 2, bwid = bw - gap, r = Math.min(4, bwid / 3);
        if (d.ghost) el(s, 'rect', { x: x, y: Y(d.ghost), width: bwid, height: h - B - Y(d.ghost), rx: r, fill: 'none', stroke: C.faint, 'stroke-width': 1.5 });
        if (d.v) el(s, 'rect', { x: x, y: Y(d.v), width: bwid, height: h - B - Y(d.v), rx: r, fill: d.hot ? C.orange : C.muted, opacity: d.dim ? 0.55 : 1 });
        if (!o.thin && o.showValues !== false && d.v) {
          var inside = o.goal && Math.abs(Y(d.v) - Y(o.goal.v)) < 22 && d.v < o.goal.v;
          text(s, x + bwid / 2, inside ? Y(d.v) + 18 : Y(d.v) - 7, o.vFmt ? o.vFmt(d.v) : d.v,
            { anchor: 'middle', fill: inside && d.hot ? C.ink : C.white, weight: 800, size: g.small ? 15 : 17, display: true });
        }
        if (o.thin) {
          if (d.label && x - lastLab > (g.small ? 30 : 38)) { text(s, x + bwid / 2, h - 7, d.label, { anchor: 'middle' }); lastLab = x; }
        } else text(s, x + bwid / 2, h - (o.subLabels ? 22 : 7), d.label, { anchor: 'middle' });
        if (o.subLabels && d.sub) text(s, x + bwid / 2, h - 6, d.sub, { anchor: 'middle', fill: d.hot ? C.orange : C.axis, size: 11, weight: 700 });
        if (d.note) text(s, x + bwid / 2, Y(Math.max(d.v || 0, d.ghost || 0)) - 8, d.note, { anchor: 'middle', fill: C.white, weight: 800, size: 13, display: true });
      });
      host.setAttribute('aria-label', o.label || '');
    });
  }

  /* hbars: horizontal stacked. opts: rows [{label, parts:[{v, kind}]}], kinds {kind: {fill, name}} */
  function hbars(host, o) {
    redraw(host, function () {
      var rows = o.rows, rh = 40, top = 6, g = svgFor(host, top + rows.length * rh), s = g.s, w = g.w;
      var L = g.small ? 62 : 76, R = 40;
      var mx = Math.max.apply(null, rows.map(function (r) { return r.parts.reduce(function (a, p) { return a + p.v; }, 0); })) || 1;
      rows.forEach(function (r, i) {
        var y = top + i * rh, x = L, tot = 0;
        text(s, L - 12, y + 19, r.label, { anchor: 'end', fill: C.white, weight: 800, size: 18, display: true });
        r.parts.forEach(function (p) {
          var pw = p.v / mx * (w - L - R); tot += p.v;
          if (pw > 0) { el(s, 'rect', { x: x, y: y + 4, width: Math.max(pw - 2, 2), height: rh - 16, rx: 3, fill: o.kinds[p.kind].fill }); x += pw; }
        });
        text(s, x + 8, y + 19, tot, { fill: C.white, weight: 800, size: 17, display: true });
      });
      host.setAttribute('aria-label', o.label || '');
    });
  }


  /* timeline: several layers on one date axis. opts: x0, x1 (Dates), yLo, yHi, yStep, yFmt, xTicks, goal {y,label},
     Optional gaps [{from,to,label}], milestones [{from,to,label,dateLabel}].
     layers: [{type:'line', data:[{x,y}], color, width} | {type:'dots', data:[{x,y,label}], color} |
              {type:'rings', data:[{x,y,label}], path:true} | {type:'now', x, y, label}], label */
  function timeline(host, o) {
    redraw(host, function () {
      var milestones = o.milestones || [], extra = milestones.length ? 100 : 0;
      var g = svgFor(host, o.h || (host.clientWidth < 520 ? 240 : 300) + extra), s = g.s, w = g.w, h = g.h;
      var L = g.small ? 34 : 44, R = g.small ? 14 : (o.rightPad || 24), T = 20 + extra, B = 28, x0 = +o.x0, x1 = +o.x1;
      function X(v) { return L + (+v - x0) / ((x1 - x0) || 1) * (w - L - R); }
      function Y(v) { return T + (1 - (v - o.yLo) / (o.yHi - o.yLo)) * (h - T - B); }
      // Missing trend data is a range, never a fabricated flat or connecting line.
      (o.gaps || []).forEach(function (gap) {
        var start = Math.max(L, X(gap.from)), end = Math.min(w - R, X(gap.to));
        if (end <= start) return;
        el(s, 'rect', { x: start, y: T, width: end - start, height: h - T - B, fill: C.faint, opacity: 0.25 });
        text(s, start + 6, h - B - 14, gap.label, { fill: C.soft, size: 12 });
      });
      // Month-wide markers avoid presenting a private or inferred exact birthday.
      milestones.forEach(function (m, i) {
        var start = X(m.from), end = X(m.to), x = (start + end) / 2;
        var y = 17 + i * 43, labelX = Math.max(L, Math.min(x, w - 145));
        text(s, labelX, y, m.label, { fill: C.soft, size: 14, weight: 700 });
        text(s, labelX, y + 18, m.dateLabel, { fill: C.axis, size: 12 });
        el(s, 'line', { x1: x, x2: x, y1: y + 24, y2: h - B, stroke: C.axis, 'stroke-dasharray': '3 5', opacity: 0.5 });
        el(s, 'rect', { x: start, y: T - 7, width: Math.max(2, end - start), height: 3, fill: C.soft });
      });
      for (var t = Math.ceil(o.yLo / o.yStep) * o.yStep; t <= o.yHi; t += o.yStep) {
        el(s, 'line', { x1: L, x2: w - R, y1: Y(t), y2: Y(t), stroke: C.grid });
        text(s, L - 8, Y(t) + 4, o.yFmt ? o.yFmt(t) : t, { anchor: 'end' });
      }
      xLabels(s, (o.xTicks || []).map(function (t) { return { x: X(t.x), label: t.label }; }), h - 8, L, w - R);
      if (o.goal) {
        el(s, 'line', { x1: L, x2: w - R, y1: Y(o.goal.y), y2: Y(o.goal.y), stroke: C.white, 'stroke-width': 1.5, 'stroke-dasharray': '6 6', opacity: 0.85 });
        text(s, L + 6, Y(o.goal.y) - 8, o.goal.label, { fill: C.white, weight: 700 });
      }
      o.layers.forEach(function (ly) {
        if (ly.type === 'line') {
          el(s, 'path', { d: ly.data.map(function (p, i) { return (i ? 'L' : 'M') + X(p.x).toFixed(1) + ' ' + Y(p.y).toFixed(1); }).join(' '),
            fill: 'none', stroke: ly.color || C.axis, 'stroke-width': ly.width || 1.5, 'stroke-linejoin': 'round', opacity: ly.opacity || 1 });
        } else if (ly.type === 'rings') {
          if (ly.path && ly.from) {
            var pts = [ly.from].concat(ly.data);
            el(s, 'path', { d: pts.map(function (p, i) { return (i ? 'L' : 'M') + X(p.x).toFixed(1) + ' ' + Y(p.y).toFixed(1); }).join(' '),
              fill: 'none', stroke: C.orange, 'stroke-width': 1.5, 'stroke-dasharray': '2 6', 'stroke-linecap': 'round', opacity: 0.8 });
          }
          ly.data.forEach(function (p) {
            var ring = el(s, 'circle', { cx: X(p.x), cy: Y(p.y), r: 6, fill: C.ink, stroke: C.orange, 'stroke-width': 2.5 });
            if (p.title) el(ring, 'title', {}, p.title);
            if (p.label && (!g.small || p.keep)) text(s, X(p.x) + (p.anchor === 'start' ? 10 : p.anchor === 'end' ? -10 : 0), Y(p.y) + (p.dy != null ? p.dy : (p.anchor === 'start' ? 4 : (p.below ? 22 : -13))), p.label, { anchor: p.anchor || 'middle', fill: C.orange, weight: 700, size: 12 });
          });
        } else if (ly.type === 'dots') {
          ly.data.forEach(function (p) {
            var dot = el(s, 'circle', { cx: X(p.x), cy: Y(p.y), r: 6, fill: C.white, stroke: C.ink, 'stroke-width': 2 });
            if (p.title) el(dot, 'title', {}, p.title);
            if (p.label && (!g.small || p.keep)) text(s, X(p.x) + (p.anchor === 'start' ? 10 : 0), Y(p.y) + (p.anchor === 'start' ? 4 : (p.below ? 22 : -13)), p.label, { anchor: p.anchor || 'middle', fill: C.white, weight: 700, size: 12 });
          });
        } else if (ly.type === 'now') {
          el(s, 'circle', { cx: X(ly.x), cy: Y(ly.y), r: 6.5, fill: C.orange, stroke: C.ink, 'stroke-width': 2 });
          text(s, X(ly.x), Y(ly.y) + 24, ly.label, { anchor: 'middle', fill: C.white, weight: 800, size: g.small ? 15 : 17, display: true });
        }
      });
      host.setAttribute('aria-label', o.label || '');
    });
  }

  window.TTF = { line: line, bars: bars, hbars: hbars, timeline: timeline, C: C,
    kit: { el: el, svgFor: svgFor, text: text, niceTicks: niceTicks, xLabels: xLabels, redraw: redraw } };   /* feed.js draws with the same parts */
})();
