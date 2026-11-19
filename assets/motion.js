// motion.js: quiet motion for tothefinish.ai (Tyler 2026-11-19: "add animation to the whole website as you scroll
// through and click links/buttons"). House rules (brain/design/current/DESIGN.md §7, kept by First Light):
// one-time 8 px fade-up as a block first enters, 150 ms presses, 200-250 ms reveals, nothing loops, reduced
// motion turns it all off, and content never depends on this file to appear (only blocks still below the fold
// are hidden, and only once this has run).
(function () {
  var nav = location.pathname.replace(/index\.html$/, '');
  [].slice.call(document.querySelectorAll('.nav a')).forEach(function (a) {
    var h = a.getAttribute('href') || '';
    if (h.charAt(0) === '/' && h.length > 1 && h.indexOf('#') < 0 && nav.indexOf(h) === 0) a.setAttribute('aria-current', 'page');
  });
  if (!window.requestAnimationFrame || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var SEL = ['section .kicker', 'section h2', 'section .wrap > p', 'section .wrap > .body', '.prose > *', '.two > *',
    '.grid > .card', '.rgrid', '.facts', '.chart', '.gap-head', '.gapline', '.ftable', 'form.join', '.rfilters',
    '.rmonth', '.eplist > li', '.qlist', '.episode > *', '.video', 'footer .sign'].join(',');
  var vh = window.innerHeight, seen = new Set(), items = [];
  [].slice.call(document.querySelectorAll(SEL)).forEach(function (el) {
    if (seen.has(el) || el.closest('header')) return;
    seen.add(el);
    if (el.getBoundingClientRect().top < vh * 0.92) return; // already on screen: leave it alone
    el.classList.add('reveal');
    // cards in one row arrive a beat apart (40 ms each, at most 200 ms)
    var sib = el.parentElement && el.parentElement.classList.contains('grid') ? [].indexOf.call(el.parentElement.children, el) : 0;
    if (sib) el.style.transitionDelay = Math.min(sib * 40, 200) + 'ms';
    items.push(el);
  });
  // reveal everything at or above the bottom of the screen, so a jump (anchor link, back button, fast fling)
  // never leaves a block hidden above you
  var left = items.slice(), ticking = false;
  function check() {
    ticking = false;
    var edge = window.innerHeight * 0.94;
    left = left.filter(function (el) {
      if (el.getBoundingClientRect().top < edge) { el.classList.add('in'); return false; }
      return true;
    });
    if (!left.length) { window.removeEventListener('scroll', onScroll); window.removeEventListener('resize', onScroll); }
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(check); } }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  check();
})();
