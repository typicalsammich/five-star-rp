import test from 'node:test';import assert from 'node:assert/strict';
let scenario=0;
async function fixture(options,check){
 const saved=new Map(),timers=new Map();let timerId=0;
 const install=(key,value)=>{saved.set(key,Object.getOwnPropertyDescriptor(globalThis,key));Object.defineProperty(globalThis,key,{configurable:true,writable:true,value})};
 class Node extends EventTarget{
  constructor(kind='div'){super();this.kind=kind;this.style={};this.dataset={};this.children=[];this.inert=false;this.currentTime=0;this.attrs={};const set=new Set();this.classList={contains:x=>set.has(x),add:(...xs)=>xs.forEach(x=>set.add(x)),remove:(...xs)=>xs.forEach(x=>set.delete(x))}}
  append(...nodes){for(const n of nodes){n.parent=this;this.children.push(n)}}
  remove(){if(this.parent)this.parent.children=this.parent.children.filter(n=>n!==this)}
  contains(n){return this.children.includes(n)}setAttribute(k,v){this.attrs[k]=v}removeAttribute(k){delete this.attrs[k]}pause(){this.paused=true}load(){}focus(){}
  getBoundingClientRect(){return {left:0,top:options.offscreen?-900:100,width:1200,height:690,bottom:options.offscreen?-210:790}}
  decode(){return options.decodeFailure?Promise.reject(new Error('bad image')):Promise.resolve()}
  async play(){if(options.playFailure)throw new Error('Autoplay blocked');this.dispatchEvent(new Event('loadeddata'));this.dispatchEvent(new Event('playing'))}
 }
 const body=new Node(),hero=new Node(),image=new Node('img'),header=new Node(),content=new Node(),bottom=new Node(),target=new Node('a');body.classList.add('home');hero.querySelector=()=>image;
 const doc=new Node();doc.body=body;doc.createElement=kind=>new Node(kind);doc.querySelector=s=>({'.hero':hero,'.header':header,'.hero-content':content,'.hero-bottom':bottom,'.hero-content .button':target}[s]);
 const mediaQuery=query=>{const q=new Node();q.matches=query.includes('reduced-motion')&&!!options.reduced;return q};
 const win=new Node();install('document',doc);install('location',{hostname:'example.com'});install('navigator',{connection:{saveData:false}});install('innerHeight',800);install('matchMedia',mediaQuery);install('getComputedStyle',()=>({objectPosition:'center'}));install('addEventListener',win.addEventListener.bind(win));
 install('sessionStorage',{getItem(){if(options.storageFailure)throw new Error('denied');return options.seen?'seen':null},setItem(){if(options.storageFailure)throw new Error('denied')}});
 install('fetch',async()=>({ok:true,json:async()=>({version:'lifecycle-test',productionReady:true,desktop:{mp4:'/movie.mp4'},mobile:{mp4:'/portrait.mp4'}})}));
 install('setTimeout',(fn,ms)=>{const id=++timerId;timers.set(id,{fn,ms});return id});install('clearTimeout',id=>timers.delete(id));
 const flush=ms=>{for(const [id,t]of [...timers])if(t.ms===ms){timers.delete(id);t.fn()}};
 try{const m=await import('../public/cinematic.js?scenario='+scenario++);await m.initializeCinematic();await check({body,hero,header,content,overlay:body.children[0],flush,video:body.children[0]?.children.find(n=>n.kind==='video')})}
 finally{for(const [key,descriptor]of saved)if(descriptor)Object.defineProperty(globalThis,key,descriptor);else delete globalThis[key]}
}
test('successful intro reveals and cleans up the video without leaving content inert',async()=>fixture({},({body,hero,header,content,video,flush})=>{assert.equal(hero.dataset.introState,'playing');assert(header.inert);video.currentTime=3.8;video.dispatchEvent(new Event('timeupdate'));assert.equal(hero.dataset.introState,'transitioning');assert(!content.inert);video.dispatchEvent(new Event('ended'));flush(340);assert.equal(hero.dataset.introState,'complete');assert.equal(body.children.length,0);assert(!header.inert);assert(!body.classList.contains('cinematic-playing'))}));
test('skip, blocked autoplay and stall restore an immediately usable homepage',async()=>{
 for(const kind of ['skip','playFailure','stall','error'])await fixture({playFailure:kind==='playFailure'},({hero,body,overlay,header,content,flush})=>{if(kind==='skip')overlay.children.at(-1).children[0].dispatchEvent(new Event('click'));if(kind==='stall'){overlay.children.find(n=>n.kind==='video').dispatchEvent(new Event('stalled'));flush(2500)}if(kind==='error')overlay.children.find(n=>n.kind==='video').dispatchEvent(new Event('error'));flush(340);assert.equal(hero.dataset.introState,kind==='skip'?'skipped':'failed');assert.equal(body.children.length,0);assert(!header.inert&&!content.inert)})
});
test('storage denial still permits playback, while seen and reduced motion avoid it',async()=>{
 await fixture({storageFailure:true},({hero,video,flush})=>{assert.equal(hero.dataset.introState,'playing');video.dispatchEvent(new Event('ended'));flush(340)});
 for(const options of [{seen:true},{reduced:true},{decodeFailure:true},{offscreen:true}])await fixture(options,({body,header,content})=>{assert.equal(body.children.length,0);assert(!header.inert&&!content.inert)});
});
