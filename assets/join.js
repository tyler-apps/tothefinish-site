(function () {
  window.dataLayer = window.dataLayer || [];
  var frame = document.getElementById('hidden_iframe');
  var pending = null;
  function formType(f) {
    if (f.dataset.formType) return f.dataset.formType;
    return f.querySelector('[name="fields[training_for]"]') ? 'waitlist' : 'follow_along';
  }
  if (frame) {
    frame.addEventListener('load', function () {
      if (!pending) return;
      var f = pending; pending = null;
      var type = formType(f);
      var params = { form_type: type, form_location: f.id.replace(/^join-/, '') };
      if (type === 'waitlist') { params.lead_source = 'waitlist'; }
      else { params.method = 'follow_along'; }
      // Sent straight to GA4 by the Google tag (G-3J00LR0ES7); no Tag Manager tags needed.
      if (typeof window.gtag === 'function') {
        window.gtag('event', type === 'waitlist' ? 'generate_lead' : 'sign_up', params);
      }
    });
  }
  document.querySelectorAll('form.join').forEach(function (f) {
    f.action = 'https://app.kit.com/forms/10209840/subscriptions';
    f.method = 'POST';
    f.target = 'hidden_iframe';
    f.addEventListener('submit', function () {
      pending = f;
      var t = document.getElementById(f.dataset.thanks);
      setTimeout(function () { f.style.display = 'none'; t.style.display = 'block'; }, 300);
    });
  });
})();
