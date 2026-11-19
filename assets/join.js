document.querySelectorAll('form.join').forEach(function(f){
  f.action='https://app.kit.com/forms/10209840/subscriptions';
  f.method='POST';
  f.target='hidden_iframe';
  f.addEventListener('submit',function(){
    var t=document.getElementById(f.dataset.thanks);
    if(window.gtag){gtag('event','sign_up',{method:'waitlist',form_location:f.id==='join-top'?'top':'bottom'});}
    setTimeout(function(){f.style.display='none';t.style.display='block';},300);
  });
});
