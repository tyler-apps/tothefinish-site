// /san-diego-races/ filters: hide rows that don't match; state lives in the address bar so a filtered list can be shared.
(function () {
  var rows = [].slice.call(document.querySelectorAll('.rrow'));
  var months = [].slice.call(document.querySelectorAll('.rmonth'));
  var q = document.getElementById('rq'), from = document.getElementById('rfrom'), to = document.getElementById('rto');
  var chips = [].slice.call(document.querySelectorAll('#rf .chip'));
  var st = { dist: [], when: 'all', plan: false, mine: false };
  var iso = function (d) { return d.toISOString().slice(0, 10); };
  var today = new Date(); today.setHours(12);

  function read() {
    var p = new URLSearchParams(location.search);
    st.dist = (p.get('d') || '').split(',').filter(Boolean);
    st.when = p.get('when') || 'all';
    st.plan = p.get('plan') === '1';
    st.mine = p.get('mine') === '1';
    q.value = p.get('q') || '';
    from.value = p.get('from') || '';
    to.value = p.get('to') || '';
  }
  function write() {
    var p = new URLSearchParams();
    if (st.dist.length) p.set('d', st.dist.join(','));
    if (st.when !== 'all') p.set('when', st.when);
    if (st.plan) p.set('plan', '1');
    if (st.mine) p.set('mine', '1');
    if (q.value.trim()) p.set('q', q.value.trim());
    if (from.value) p.set('from', from.value);
    if (to.value) p.set('to', to.value);
    var s = p.toString();
    history.replaceState(null, '', location.pathname + (s ? '?' + s : ''));
  }
  function apply() {
    var lo = from.value || '', hi = to.value || '';
    if (st.when !== 'all') {
      var e = new Date(today); e.setDate(e.getDate() + Number(st.when));
      lo = iso(today); hi = iso(e);
    }
    var words = q.value.toLowerCase().trim().split(/\s+/).filter(Boolean), shown = 0;
    rows.forEach(function (r) {
      var ok = true, d = r.dataset.date;
      if (st.dist.length && !st.dist.some(function (x) { return (' ' + r.dataset.d + ' ').indexOf(' ' + x + ' ') > -1; })) ok = false;
      if (lo && d < lo) ok = false;
      if (hi && d > hi) ok = false;
      if (st.plan && r.dataset.plan !== '1') ok = false;
      if (st.mine && r.dataset.mine !== '1') ok = false;
      if (words.length && !words.every(function (w) { return r.dataset.name.indexOf(w) > -1; })) ok = false;
      r.hidden = !ok; if (ok) shown++;
    });
    months.forEach(function (m) { m.hidden = !m.querySelector('.rrow:not([hidden])'); });
    chips.forEach(function (c) {
      var on = c.dataset.dist ? st.dist.indexOf(c.dataset.dist) > -1
        : c.dataset.when ? (st.when === c.dataset.when && !(c.dataset.when === 'all' && (from.value || to.value)))
        : st[c.dataset.flag];
      c.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    document.getElementById('rn').textContent = shown;
    document.getElementById('rnl').textContent = shown === 1 ? 'race' : 'races';
    document.getElementById('rempty').hidden = shown > 0;
    var any = st.dist.length || st.when !== 'all' || st.plan || st.mine || q.value.trim() || from.value || to.value;
    document.getElementById('rclear').hidden = !any;
    write();
  }
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      if (c.dataset.dist) {
        var i = st.dist.indexOf(c.dataset.dist);
        if (i > -1) st.dist.splice(i, 1); else st.dist.push(c.dataset.dist);
      } else if (c.dataset.when) {
        st.when = c.dataset.when; from.value = ''; to.value = '';
      } else { st[c.dataset.flag] = !st[c.dataset.flag]; }
      apply();
    });
  });
  [from, to].forEach(function (el) { el.addEventListener('change', function () { st.when = 'all'; apply(); }); });
  q.addEventListener('input', apply);
  document.getElementById('rclear').addEventListener('click', function () {
    st = { dist: [], when: 'all', plan: false, mine: false }; q.value = ''; from.value = ''; to.value = ''; apply();
  });
  // "Training for this one?" picks that race in the waitlist's race picker and jumps to it
  [].slice.call(document.querySelectorAll('.rtrain')).forEach(function (a) {
    a.addEventListener('click', function () {
      var f = document.getElementById('race-races');
      if (f) { f.value = a.dataset.race; setTimeout(function () { f.focus({ preventScroll: true }); }, 350); }
    });
  });
  read(); apply();
})();
