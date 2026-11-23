import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
import assert from 'node:assert/strict';
const source=readFileSync(new URL('../assets/watch-story.js',import.meta.url),'utf8');
function setup({reduced=false,mobile=false}={}){
 const listeners={},pref={matches:reduced,addEventListener(_,fn){this.change=fn}},phone={matches:mobile},classes=new Set(),frames=[];
 let tops=[100,700,1300,1900];
 const chapters=tops.map((_,i)=>({getBoundingClientRect:()=>({top:tops[i]})}));
 const links=tops.map(()=>({attrs:{},setAttribute(k,v){this.attrs[k]=v},removeAttribute(k){delete this.attrs[k]},addEventListener(_,fn){this.click=fn}}));
 const root={dataset:{},style:{setProperty(){}},classList:{toggle(k,on){on?classes.add(k):classes.delete(k)}},querySelectorAll(q){return q.includes('step')?chapters:links},querySelector(q){return q==='.watch-sticky'?{getBoundingClientRect:()=>({bottom:400})}:null}};
 runInNewContext(source,{document:{getElementById:()=>root},window:{matchMedia:q=>q.includes('reduced')?pref:phone,addEventListener(k,fn){listeners[k]=fn},removeEventListener(k){delete listeners[k]}},innerHeight:844,requestAnimationFrame:fn=>(frames.push(fn),frames.length),cancelAnimationFrame(){frames.length=0}});
 return {root,links,pref,classes,listeners,frames,setTops(t){tops=t},flush(){while(frames.length)frames.shift()()}};
}
const s=setup();assert.equal(s.root.dataset.stage,'0');
s.setTops([-1300,-700,-100,500]);s.listeners.scroll();s.listeners.scroll();assert.equal(s.frames.length,1);s.flush();assert.equal(s.root.dataset.stage,'2');assert.equal(s.links[2].attrs['aria-current'],'step');assert.equal(s.links[0].attrs['aria-current'],undefined);
s.setTops([-1900,-1300,-700,-100]);s.listeners.scroll();s.flush();assert.equal(s.root.dataset.stage,'3');
s.pref.matches=true;s.pref.change();assert.equal(s.root.dataset.stage,'0');assert.equal(s.listeners.scroll,undefined);assert.equal(s.classes.has('is-enhanced'),false);
s.links[2].click();assert.equal(s.root.dataset.stage,'2'); // keyboard/native link still selects without animation
s.pref.matches=false;s.pref.change();assert.equal(s.root.dataset.stage,'3');
const m=setup({mobile:true});m.setTops([-800,-200,416,1000]);m.listeners.scroll();m.flush();assert.equal(m.root.dataset.stage,'2');
const r=setup({reduced:true});assert.equal(r.listeners.scroll,undefined);assert.equal(r.classes.has('is-enhanced'),false);
const h=readFileSync(new URL('../index.html',import.meta.url),'utf8');const d=JSON.parse(readFileSync(new URL('../data/watch-story.json',import.meta.url),'utf8'));
for(const value of [d.distance_mi,d.duration,d.avg_hr,d.climb_ft,d.recovery.overnight_hrv_ms,d.recovery.garmin_seven_day_hrv_ms])assert.ok(h.includes(String(value)));
assert.equal(d.date,'2026-11-23');assert.equal(d.recovery.nights.length,7);assert.equal(d.recovery.nights.at(-1).hrv_ms,85);
assert.equal(/walking/i.test(h.split('<!-- WATCH STORY START -->')[1].split('<!-- WATCH STORY END -->')[0]),false);
assert.equal(JSON.stringify(d).includes('latitude'),false);assert.equal(JSON.stringify(d).includes('longitude'),false);
assert.ok(h.includes('href="#inside"'));assert.ok(h.includes('id="how"'));assert.ok(h.includes('id="research"'));
console.log('PASS: four scroll stages, coalesced frames, mobile stage offset, reduced-motion entry/live changes, native selection, dated real values and no coordinates');
