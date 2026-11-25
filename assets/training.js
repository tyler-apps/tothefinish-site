/* Progressive enhancement: the whole journal is readable without JavaScript. */
(function(){
  'use strict';
  var filters=document.querySelector('.training-filters');
  if(filters){
    var entries=Array.from(document.querySelectorAll('.training-entry'));
    filters.hidden=false;
    filters.addEventListener('click',function(event){
      var button=event.target.closest('button[data-filter]'); if(!button)return;
      var kind=button.dataset.filter, count=0;
      filters.querySelectorAll('button').forEach(function(b){b.setAttribute('aria-pressed',String(b===button));});
      entries.forEach(function(entry){entry.hidden=kind!=='all'&&entry.dataset.kind!==kind;if(!entry.hidden)count++;});
      document.querySelector('#training-count').textContent=count+' recorded '+(kind==='all'?'sessions':kind==='run'?'runs':'strength sessions');
      document.querySelector('#training-empty').hidden=count!==0;
    });
  }
  var preview=document.querySelector('#training-preview-latest');
  if(!preview)return;
  fetch('/data/training.json',{cache:'no-cache'}).then(function(r){if(!r.ok)throw Error('unavailable');return r.json();}).then(function(data){
    var latest=data.sessions&&data.sessions[0]; if(!latest)return;
    var label=new Intl.DateTimeFormat('en-US',{month:'short',day:'numeric',year:'numeric',timeZone:'UTC'});
    preview.querySelector('[data-training-date]').textContent=label.format(new Date(latest.date+'T12:00:00Z'))+' · '+(latest.kind==='run'?'run':'strength')+' recorded';
    preview.querySelector('[data-training-title]').textContent=latest.title;
    preview.querySelector('[data-training-miles]').textContent=String(data.week.recorded_miles);
    preview.querySelector('[data-training-plan]').textContent=data.week.planned_miles==null?'Not set':String(data.week.planned_miles);
    preview.querySelector('[data-training-note]').textContent=latest.review?latest.review.decision:'The journal keeps the recorded work and reviewed coaching notes together.';
    preview.querySelector('[data-training-link]').href='/training/#'+encodeURIComponent(latest.key);
    preview.querySelector('[data-training-asof]').textContent='Records checked '+label.format(new Date(data.as_of+'T12:00:00Z'))+'.';
  }).catch(function(){/* Keep the explicitly dated, readable saved preview and journal link. */});
})();
