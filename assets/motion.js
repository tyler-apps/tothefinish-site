// motion.js: motion for tothefinish.ai.
// 2026-11-19, Tyler: "add animation to the whole website as you scroll through and click links/buttons", then
// "harder animation and i want the charts/graphs animated". His call overrides the quiet-motion default for this
// site (brain/design/tylerstewarttrains/DESIGN.md §8). Still: reduced motion turns it all off, nothing loops, and
// content never depends on this file (only blocks still below the fold get hidden, and only once this runs).
(function () {
  var path = location.pathname.replace(/index\.html$/, '');
  [].slice.call(document.querySelectorAll('.nav a')).forEach(function (a) {
    var h = a.getAttribute('href') || '';
    if (h.charAt(0) === '/' && h.length > 1 && h.indexOf('#') < 0 && path.indexOf(h) === 0) a.setAttribute('aria-current', 'page');
  });
  if (!window.requestAnimationFrame || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.documentElement.classList.add('motion');

  // 1. the page opens: header lines rise in one after another
  [].slice.call(document.querySelectorAll('header .kicker, header h1, header .lead, header .page > p.body, .top .hero > *'))
    .forEach(function (el, i) { el.classList.add('intro'); el.style.animationDelay = (80 + i * 90) + 'ms'; });

  // 2. blocks below the fold rise in as they arrive; grids and lists arrive item by item
  var SEL = ['section .kicker', 'section h2', 'section .wrap > p', '.prose > *', '.two > *', '.gap-head', '.gapline',
    '.chart', '.ftable', 'form.join', '.rfilters', '.rmonth h2', '.episode > *', '.video', 'footer .sign'].join(',');
  var GROUPS = '.grid, .rgrid, .facts, .rlist, .eplist, .qlist, .ftable tbody';
  var vh = window.innerHeight, seen = new Set(), items = [];
  function mark(el, delay) {
    if (seen.has(el) || el.closest('header')) return;
    seen.add(el);
    if (el.getBoundingClientRect().top < vh * 0.9) return; // on screen already: leave it
    el.classList.add('reveal');
    // the race list is for finding a race fast (Tyler 2026-11-19): short, no stagger, in before it reaches the screen
    if (el.closest('.rlist, .rmonth')) { el.classList.add('quick'); delay = 0; }
    if (delay) el.style.transitionDelay = delay + 'ms';
    items.push(el);
  }
  [].slice.call(document.querySelectorAll(SEL)).forEach(function (el) { mark(el, 0); });
  [].slice.call(document.querySelectorAll(GROUPS)).forEach(function (g) {
    [].slice.call(g.children).forEach(function (el, i) { mark(el, Math.min(i, 8) * 70); });
  });

  // 3. charts draw themselves once they are on screen and drawn (the home charts arrive after a data fetch)
  var charts = [].slice.call(document.querySelectorAll('.chart svg')).map(function (svg) {
    var c = { svg: svg, seen: false, ready: svg.childElementCount > 0, done: false, t: 0 };
    new MutationObserver(function () {
      clearTimeout(c.t);
      c.t = setTimeout(function () { c.ready = true; play(c); }, 120);
    }).observe(svg, { childList: true });
    return c;
  });
  function play(c) {
    if (c.done || !c.ready || !c.seen || !c.svg.animate) return;
    c.done = true;
    var base = 250, nodes = [].slice.call(c.svg.querySelectorAll('*'));
    var bars = nodes.filter(function (n) { return n.tagName === 'rect' && +n.getAttribute('height') > 0 && +n.getAttribute('width') < 200; });
    bars.sort(function (a, b) { return (+a.getAttribute('x')) - (+b.getAttribute('x')); });
    bars.forEach(function (r, i) {
      r.style.transformBox = 'fill-box'; r.style.transformOrigin = '50% 100%';
      r.animate([{ transform: 'scaleY(0)' }, { transform: 'scaleY(1)' }],
        { duration: 700, delay: base + i * 18, easing: 'cubic-bezier(.16,1,.3,1)', fill: 'backwards' });
    });
    var lineEnd = base;
    nodes.forEach(function (n) {
      if (!/^(path|polyline|line)$/.test(n.tagName)) return;
      var cs = getComputedStyle(n);
      var filled = n.tagName === 'path' && cs.fill !== 'none' && cs.fill !== 'transparent' && cs.fill !== 'rgba(0, 0, 0, 0)';
      if (cs.stroke === 'none' || filled) {
        n.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 900, delay: base + 600, fill: 'backwards' });
        return;
      }
      var dashed = cs.strokeDasharray && cs.strokeDasharray !== 'none';
      var len = n.getTotalLength ? n.getTotalLength() : 0;
      if (n.tagName === 'line' && !dashed && n.getAttribute('y1') === n.getAttribute('y2')) return; // gridlines stay put
      if (dashed || !len) {
        n.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 600, delay: base + 900, fill: 'backwards' });
        return;
      }
      var dur = Math.min(1800, 600 + len * 0.9);
      n.style.strokeDasharray = len; // cleared when done so the line reads exactly as drawn
      var a = n.animate([{ strokeDashoffset: len }, { strokeDashoffset: 0 }],
        { duration: dur, delay: base, easing: 'cubic-bezier(.65,0,.35,1)', fill: 'backwards' });
      a.onfinish = function () { n.style.strokeDasharray = ''; };
      lineEnd = Math.max(lineEnd, base + dur);
    });
    var after = Math.max(lineEnd - 200, base + bars.length * 18 + 300);
    nodes.forEach(function (n) {
      if (n.tagName === 'circle') {
        n.style.transformBox = 'fill-box'; n.style.transformOrigin = 'center';
        n.animate([{ transform: 'scale(0)' }, { transform: 'scale(1.35)', offset: .7 }, { transform: 'scale(1)' }],
          { duration: 500, delay: after, easing: 'ease-out', fill: 'backwards' });
      } else if (n.tagName === 'text') {
        n.animate([{ opacity: 0, transform: 'translateY(6px)' }, { opacity: 1, transform: 'none' }],
          { duration: 450, delay: n.getAttribute('class') === 't' ? after : base + 100, easing: 'ease-out', fill: 'backwards' });
      }
    });
  }

  // reveal everything at or above the bottom of the screen, so a jump (anchor link, back button, fast fling)
  // never leaves a block hidden above you
  var left = items.slice(), ticking = false;
  function check() {
    ticking = false;
    var edge = window.innerHeight * 0.92, early = window.innerHeight * 1.15;
    left = left.filter(function (el) {
      if (el.getBoundingClientRect().top < (el.classList.contains('quick') ? early : edge)) { el.classList.add('in'); return false; }
      return true;
    });
    charts.forEach(function (c) {
      if (!c.seen && c.svg.getBoundingClientRect().top < window.innerHeight * 0.85) { c.seen = true; play(c); }
    });
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(check); } }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  document.addEventListener('input', onScroll);   // a race filter can pull rows onto the screen
  document.addEventListener('click', onScroll);
  check();
})();
