/* Shared motion, keyboard navigation and anonymous intent events. No scroll hijacking.
   Content is visible without JS. Reduced motion can be changed while the page is open. */
(function () {
  'use strict';
  var menus = document.querySelectorAll('.mnav');
  function closeMenus(restore) { menus.forEach(function (d) { if (d.open) { d.open = false; if (restore) d.querySelector('summary').focus(); } }); }
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenus(true); });
  document.addEventListener('click', function (e) {
    menus.forEach(function (d) { if (!d.contains(e.target) || e.target.closest('a')) d.open = false; });
    var a = e.target.closest('a');
    if (!a || typeof window.gtag !== 'function') return;
    var path = a.getAttribute('href') || '', event;
    if (/^\/episodes\/[^#]+|youtube\.com\/watch/.test(path)) event = 'watch_click';
    else if (/^\/coaches\//.test(path)) event = 'coach_explore';
    if (event) window.gtag('event', event, { link_path: path, transport_type: 'beacon' });
  });
  var pref = window.matchMedia('(prefers-reduced-motion: reduce)'), observer, chartObserver, mutations;
  var animations = new Set(), seenCharts = new WeakSet(), ticking = false;
  var progress = document.createElement('div'); progress.className = 'read-progress'; progress.setAttribute('aria-hidden', 'true'); document.body.appendChild(progress);
  function track(a) { animations.add(a); a.onfinish = function () { animations.delete(a); }; }
  function draw(container) {
    if (pref.matches) return;
    var svg = container.querySelector('svg');
    if (!svg || seenCharts.has(svg) || !svg.animate) return;
    seenCharts.add(svg);
    container.dataset.motionPlayed = 'true';
    svg.querySelectorAll('rect').forEach(function (r, i) {
      if (+r.getAttribute('height') <= 0 || +r.getAttribute('width') > 200) return;
      r.style.transformBox = 'fill-box'; r.style.transformOrigin = 'center bottom';
      track(r.animate([{transform:'scaleY(0)'},{transform:'scaleY(1)'}],{duration:800,delay:Math.min(i*12,500),easing:'cubic-bezier(.16,1,.3,1)',fill:'backwards'}));
    });
    svg.querySelectorAll('path,polyline').forEach(function (p) {
      var css = getComputedStyle(p), length = p.getTotalLength ? p.getTotalLength() : 0;
      if (length && css.stroke !== 'none' && css.fill === 'none' && css.strokeDasharray === 'none') {
        // Keyframes, not inline dash styles: cancellation restores the exact original chart.
        track(p.animate([{strokeDasharray:length+' '+length,strokeDashoffset:length},{strokeDasharray:length+' '+length,strokeDashoffset:0}],{duration:1400,easing:'ease-in-out'}));
      } else track(p.animate([{opacity:0},{opacity:1}],{duration:700,delay:250,fill:'backwards'}));
    });
    svg.querySelectorAll('circle').forEach(function (c) { track(c.animate([{opacity:0},{opacity:1}],{duration:500,delay:650,fill:'backwards'})); });
  }
  function readProgress() {
    ticking = false;
    if (pref.matches) return;
    var total = document.documentElement.scrollHeight - innerHeight;
    progress.style.transform = 'scaleX(' + (total > 0 ? Math.min(1, Math.max(0, scrollY/total)) : 0) + ')';
    document.querySelectorAll('.road').forEach(function (r) {
      var box = r.getBoundingClientRect(), amount = Math.min(1,Math.max(0,(innerHeight*.8-box.top)/(Math.min(box.height,innerHeight)*.8)));
      r.style.setProperty('--road-progress',amount);
    });
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(readProgress); } }
  function showTarget(e) {
    var el = e && e.target instanceof Element ? e.target : null;
    if (!el && location.hash) el = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (el) { var p = el; while (p) { p.classList.add('in'); p = p.parentElement; } el.querySelectorAll('.reveal').forEach(function(n){n.classList.add('in');}); }
  }
  function stop() {
    if (observer) observer.disconnect(); if (chartObserver) chartObserver.disconnect(); if (mutations) mutations.disconnect();
    animations.forEach(function(a){a.cancel();}); animations.clear();
    document.querySelectorAll('.reveal').forEach(function(n){n.classList.add('in');});
    document.documentElement.classList.remove('motion');
    window.removeEventListener('scroll',onScroll); window.removeEventListener('resize',onScroll);
  }
  function start() {
    if (pref.matches || !window.IntersectionObserver) return;
    document.documentElement.classList.add('motion');
    observer = new IntersectionObserver(function(entries){entries.forEach(function(entry){if(entry.isIntersecting){entry.target.classList.add('in');observer.unobserve(entry.target);}});},{rootMargin:'0px 0px 6% 0px',threshold:0});
    // Animate a card as a unit; nested reveals produce multiple unnecessary delays.
    var selectors = 'section .kicker,section h2,section .wrap > .body,.wrap.cols > div,.coaches > *, .facts > *, .road > *, .viz, .vizgrid > *, .prose > *, .eplist > *, .qlist > *, .joincard, .coachhead, .feed-grid > *, .rlist > *, .rgrid > *';
    var targets = Array.from(document.querySelectorAll(selectors));
    targets.forEach(function(el){
      if (el.parentElement.closest('.prose,.viz,.coach,.joincard') || targets.some(function(other){return other!==el && other.contains(el);})) return;
      if (el.getBoundingClientRect().top < innerHeight*.95) return;
      el.classList.add('reveal'); el.classList.remove('in');
      var parent=el.parentElement;
      if (parent.matches('.coaches,.facts,.road,.vizgrid')) el.style.transitionDelay = Math.min(Array.from(parent.children).indexOf(el)*80,320)+'ms';
      observer.observe(el);
    });
    chartObserver=new IntersectionObserver(function(entries){entries.forEach(function(e){if(e.isIntersecting)draw(e.target);});},{threshold:.1});
    var plots=document.querySelectorAll('.plot,.chart');
    plots.forEach(function(p){chartObserver.observe(p);});
    mutations=new MutationObserver(function(){plots.forEach(function(p){var b=p.getBoundingClientRect();if(b.top<innerHeight&&b.bottom>0)draw(p);});});
    plots.forEach(function(p){mutations.observe(p,{childList:true,subtree:true});});
    window.addEventListener('scroll',onScroll,{passive:true}); window.addEventListener('resize',onScroll);
    showTarget(); readProgress();
  }
  document.addEventListener('focusin',showTarget); window.addEventListener('hashchange',function(){showTarget();});
  window.addEventListener('beforeprint',stop); window.addEventListener('afterprint',start);
  pref.addEventListener('change',function(){stop();start();});
  start();
})();
