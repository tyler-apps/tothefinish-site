/* join.js: every sign-up form on the site. The form posts to Kit inside a hidden iframe, so the page never leaves.
   2026-11-21 review fix: the thank-you shows when the iframe finishes loading Kit's answer (it used to show 300 ms
   after the click, whatever happened). No answer in 8 seconds shows one plain error line with a retry. The GA4
   event (sign_up for the Sunday letter, generate_lead for the waitlist) fires on that load, once per submit.
   A cross-origin iframe can't say what Kit answered, only that an answer came back. */
(function () {
  window.dataLayer = window.dataLayer || [];
  var frame = document.getElementById('hidden_iframe');
  var WAIT_MS = 8000;
  // one thank-you per kind of form, wherever the form sits
  var THANKS = {
    follow_along: "You're in. The first letter comes Sunday night.",
    waitlist: "You're on the waitlist. If the coaches get me to Chicago, you're first to try them."
  };
  var pending = null;   // the submit in flight: { form, timer, done }

  function formType(f) {
    if (f.dataset.formType) return f.dataset.formType;
    return f.querySelector('[name="fields[training_for]"]') ? 'waitlist' : 'follow_along';
  }
  function submitBtn(f) { return f.querySelector('button[type="submit"]'); }
  function errBox(f) {
    var e = f.nextElementSibling;
    if (e && e.classList.contains('formerr')) return e;
    e = document.createElement('p');
    e.className = 'formerr';
    e.setAttribute('role', 'alert');
    e.hidden = true;
    e.appendChild(document.createTextNode("That didn't go through. Check your connection, then "));
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = 'try again';
    b.addEventListener('click', function () {
      if (f.requestSubmit) f.requestSubmit(submitBtn(f)); else submitBtn(f).click();
    });
    e.appendChild(b);
    e.appendChild(document.createTextNode('.'));
    f.parentNode.insertBefore(e, f.nextSibling);
    return e;
  }
  function busy(f, on) {
    var b = submitBtn(f);
    if (!b) return;
    if (on) { b.dataset.label = b.textContent; b.textContent = 'Sending'; b.disabled = true; }
    else { if (b.dataset.label) b.textContent = b.dataset.label; b.disabled = false; }
  }
  function fail(p) {
    busy(p.form, false);
    errBox(p.form).hidden = false;
  }
  function succeed(p) {
    if (p.done) return;
    p.done = true;
    clearTimeout(p.timer);
    var f = p.form, type = formType(f), t = document.getElementById(f.dataset.thanks);
    errBox(f).hidden = true;
    f.style.display = 'none';
    if (t) {
      if (THANKS[type]) t.textContent = THANKS[type];
      t.setAttribute('role', 'status');
      t.style.display = 'block';
    }
    var params = { form_type: type, form_location: f.id.replace(/^join-/, '') };
    if (type === 'waitlist') { params.lead_source = 'waitlist'; }
    else { params.method = 'follow_along'; }
    var pick = f.querySelector('select[name="fields[training_for]"]');
    if (pick && pick.value) { params.race_pick = pick.selectedOptions[0].classList.contains('else') ? 'Something else' : pick.value; }  // typed text never goes to GA4
    // Sent straight to GA4 by the Google tag (G-3J00LR0ES7); no Tag Manager tags needed.
    if (typeof window.gtag === 'function') {
      window.gtag('event', type === 'waitlist' ? 'generate_lead' : 'sign_up', params);
    }
  }
  if (frame) {
    frame.addEventListener('load', function () {
      if (!pending) return;          // the empty frame's own first load
      var p = pending; pending = null;
      succeed(p);                    // a late answer after the 8 s error still counts, once
    });
  }
  document.querySelectorAll('form.join').forEach(function (f) {
    f.action = 'https://app.kit.com/forms/10209840/subscriptions';
    f.method = 'POST';
    if (!frame) return;              // no frame on the page: the form posts to Kit the plain way
    f.target = 'hidden_iframe';
    f.addEventListener('submit', function (ev) {
      // race picker: "Something else" carries the typed race in the same Kit field (training_for)
      var sel = f.querySelector('select[name="fields[training_for]"]'), other = f.querySelector('input.other');
      if (sel && other && sel.selectedOptions[0] && sel.selectedOptions[0].classList.contains('else') && other.value.trim()) {
        sel.selectedOptions[0].value = 'Something else: ' + other.value.trim();
      }
      if (pending) clearTimeout(pending.timer);
      errBox(f).hidden = true;
      if (navigator.onLine === false) { ev.preventDefault(); pending = null; errBox(f).hidden = false; return; }
      var p = { form: f, done: false, timer: 0 };
      pending = p;
      p.timer = setTimeout(function () { if (!p.done) fail(p); }, WAIT_MS);
      setTimeout(function () { if (!p.done) busy(f, true); }, 0);   // after the browser has taken the form data
    });
  });
})();
