import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
const code=readFileSync(new URL('../assets/coach-film.js',import.meta.url),'utf8');
async function setup({reduced=false,blocked=false}={}){
 const listeners={};
 const el=()=>({hidden:true,textContent:'',addEventListener(name,fn){this[name]=fn;}});
 const play=el(),sound=el();
 const film={muted:false,paused:true,ended:false,currentTime:12,loop:false,autoplay:false,
  addEventListener(name,fn){listeners[name]=fn;},
  async play(){if(blocked)throw Error('autoplay blocked');this.paused=false;listeners.play?.();},
  pause(){this.paused=true;listeners.pause?.();}};
 const pref={matches:reduced,addEventListener(name,fn){this[name]=fn;}};
 runInNewContext(code,{document:{querySelector:s=>s==='.film-media video'?film:s==='.film-play'?play:sound},matchMedia:()=>pref});
 await Promise.resolve();await Promise.resolve();return {film,play,sound,pref,listeners};
}
let x=await setup();assert.equal(x.film.paused,false);assert.equal(x.film.muted,true);assert.equal(x.play.hidden,true);assert.equal(x.sound.hidden,false);
await x.sound.click();assert.equal(x.film.muted,false);assert.equal(x.film.currentTime,0);assert.equal(x.film.loop,false);assert.equal(x.sound.textContent,'Sound off');
x.sound.click();assert.equal(x.film.muted,true);
x.pref.matches=true;x.pref.change();assert.equal(x.film.paused,true);assert.equal(x.play.hidden,false);
x=await setup({reduced:true});assert.equal(x.film.paused,true);assert.equal(x.film.autoplay,false);await x.play.click();assert.equal(x.film.paused,false);assert.equal(x.film.muted,false);
x=await setup({blocked:true});assert.equal(x.play.hidden,false);assert.equal(x.sound.hidden,false);
console.log('PASS: muted autoplay, sound restart, pause fallback, reduced-motion preference and blocked-autoplay fallback');
