// Regression checks for user-facing failures, without submitting to Kit.
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
import assert from 'node:assert/strict';
const join = readFileSync(new URL('../assets/join.js',import.meta.url),'utf8');
function signup(online) {
  const handlers={},events=[],errors=[];
  const form={id:'join-test',target:'old-frame',removeAttribute(k){delete this[k]},querySelector(){return null},appendChild(n){errors.push(n)},addEventListener(k,fn){handlers[k]=fn}};
  runInNewContext(join,{document:{querySelectorAll:()=>[form],createElement:()=>({setAttribute(){}})},navigator:{onLine:online},window:{gtag:(...v)=>events.push(v)}});
  let prevented=false; handlers.submit({preventDefault(){prevented=true}});
  return {form,events,errors,prevented};
}
const offline=signup(false);
assert.equal(offline.prevented,true); assert.equal(offline.events.length,0); assert.match(offline.errors[0].textContent,/offline/);
const online=signup(true);
assert.equal(online.prevented,false); assert.equal(online.form.target,undefined);
assert.equal(online.events[0][1],'newsletter_submit');
assert.equal(JSON.stringify(online.events).includes('email'),false);
assert.equal(online.events.some(e=>e[1]==='sign_up'),false);
// Reduced motion must work at entry and when a user changes the OS preference.
const listeners={},winListeners={},classes=new Set();
const pref={matches:true,addEventListener(k,fn){listeners[k]=fn}};
let observers=0,disconnected=0;
class Observer{constructor(){observers++} observe(){} disconnect(){disconnected++}}
const context={window:{matchMedia:()=>pref,IntersectionObserver:Observer,addEventListener(k,fn){winListeners[k]=fn},removeEventListener(){}},
 document:{querySelectorAll:()=>[],createElement:()=>({style:{},setAttribute(){}}),body:{appendChild(){}},documentElement:{classList:{add:k=>classes.add(k),remove:k=>classes.delete(k)},scrollHeight:2000},addEventListener(){}},
 IntersectionObserver:Observer,MutationObserver:Observer,innerHeight:800,scrollY:0,location:{hash:''},Element:class{},requestAnimationFrame:fn=>fn()};
runInNewContext(readFileSync(new URL('../assets/motion.js',import.meta.url),'utf8'),context);
assert.equal(observers,0); assert.equal(classes.has('motion'),false);
pref.matches=false; listeners.change(); assert.equal(classes.has('motion'),true);assert.ok(observers>0);
pref.matches=true;listeners.change();assert.equal(classes.has('motion'),false);assert.ok(disconnected>0);
console.log('PASS: offline signup, native Kit response, intent-only analytics, no personal fields, reduced-motion entry and live changes');
