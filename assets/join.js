/* Native Kit POST: Kit displays the actual response. Never infer subscription success
   from a cross-origin iframe load. This event measures intent, not confirmed subscribers. */
(function () {
  document.querySelectorAll('form.join').forEach(function (form) {
    form.removeAttribute('target');
    form.addEventListener('submit', function (event) {
      var error = form.querySelector('.formerr');
      if (error) error.remove();
      if (navigator.onLine === false) {
        event.preventDefault();
        error = document.createElement('p'); error.className = 'formerr'; error.setAttribute('role','alert');
        error.textContent = 'You appear to be offline. Reconnect, then try again.'; form.appendChild(error); return;
      }
      if (typeof window.gtag === 'function') window.gtag('event','newsletter_submit',{
        form_location:form.id,method:'kit',transport_type:'beacon'
      });
      // Leave browser validation, submission, errors and provider confirmation intact.
    });
  });
})();
