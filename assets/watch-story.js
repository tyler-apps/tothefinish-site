/* Scroll selects a real, dated example. No generated measurements or live-service claims. */
(function () {
  'use strict';
  var root = document.getElementById('inside');
  if (!root) return;
  var chapters = Array.from(root.querySelectorAll('[data-watch-step]'));
  var links = Array.from(root.querySelectorAll('[data-watch-go]'));
  var preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  var phone = window.matchMedia('(max-width:760px)');
  var evidence = root.querySelector('#inside-evidence');
  var evidenceLink = root.querySelector('a[href="#inside-evidence"]');
  if (evidence && evidenceLink) evidenceLink.addEventListener('click', function () { evidence.open = true; });
  var frame = null, enabled = false;
  function select(index) {
    index = Math.max(0, Math.min(chapters.length - 1, index));
    root.dataset.stage = String(index);
    root.style.setProperty('--stage-progress', String(index / (chapters.length - 1)));
    links.forEach(function (link, i) {
      if (i === index) link.setAttribute('aria-current', 'step');
      else link.removeAttribute('aria-current');
    });
  }
  function update() {
    frame = null;
    if (!enabled) return;
    var stickyBottom = root.querySelector('.watch-sticky').getBoundingClientRect().bottom;
    var threshold = phone.matches ? Math.min(innerHeight - 80, Math.max(140, stickyBottom + 75)) : innerHeight * .52;
    var index = 0;
    chapters.forEach(function (chapter, i) { if (chapter.getBoundingClientRect().top <= threshold) index = i; });
    select(index);
  }
  function scroll() { if (frame === null) frame = requestAnimationFrame(update); }
  links.forEach(function (link, index) {
    link.addEventListener('click', function () { select(index); });
  });
  function configure() {
    enabled = !preference.matches;
    root.classList.toggle('is-enhanced', enabled);
    window.removeEventListener('scroll', scroll);
    window.removeEventListener('resize', scroll);
    if (frame !== null) { cancelAnimationFrame(frame); frame = null; }
    if (enabled) { window.addEventListener('scroll', scroll, {passive:true}); window.addEventListener('resize', scroll); update(); }
    else select(0);
  }
  preference.addEventListener('change', configure);
  configure();
})();
