export function eligible({home,reducedMotion,saveData,slowConnection,seen,hasMedia}){return home&&!reducedMotion&&!saveData&&!slowConnection&&!seen&&hasMedia}
let sessionSeen=false;
export async function initializeCinematic(){
 if(!document.body.classList.contains('home'))return;
 const hero=document.querySelector('.hero'),image=hero?.querySelector('.hero-image');if(!image)return;
 const reduce=matchMedia('(prefers-reduced-motion:reduce)'),mobile=matchMedia('(max-width:700px)');
 let config;try{const r=await fetch('/cinematic.json');if(!r.ok)return;config=await r.json()}catch{return}
 const development=['localhost','127.0.0.1'].includes(location.hostname);
 // Draft footage is available locally; only approved final footage runs in production.
 if(!config.productionReady&&!development)return;
 const storageKey='five-star-intro:'+(config.version||'original');let seen=sessionSeen;try{seen=seen||sessionStorage.getItem(storageKey)==='seen'}catch{}
 let running=false;const replay=development?document.createElement('button'):null;
 if(replay){replay.className='intro-replay';replay.textContent=config.productionReady?'Replay intro':'Preview draft intro';document.querySelector('.hero-bottom')?.append(replay)}
 async function play(manual=false){
  const media=mobile.matches?config.mobile:config.desktop;
  if(!manual&&hero.getBoundingClientRect().bottom<innerHeight*.6)return;
  if(running||reduce.matches||(!manual&&!eligible({home:true,reducedMotion:reduce.matches,saveData:!!navigator.connection?.saveData,slowConnection:['slow-2g','2g','3g'].includes(navigator.connection?.effectiveType),seen,hasMedia:config.productionReady&&!!media?.mp4})))return;
  if(!media?.mp4)return;running=true;hero.dataset.introState='loading';
  try{await image.decode()}catch{running=false;hero.dataset.introState='failed';return}
  if(reduce.matches){running=false;hero.dataset.introState='skipped';return}
  const overlay=document.createElement('div');overlay.className='cinematic-overlay';overlay.style.opacity='0';overlay.setAttribute('aria-label','Inside the Flow introduction');
  const video=document.createElement('video');video.muted=true;video.playsInline=true;video.preload='auto';video.disablePictureInPicture=true;video.setAttribute('aria-hidden','true');video.src=media.mp4;
  const shade=document.createElement('div');shade.className='cinematic-shade hero-shade';const controls=document.createElement('div');controls.className='cinematic-controls';const skip=document.createElement('button');skip.textContent='Skip Intro';controls.append(skip);overlay.append(video,shade,controls);document.body.append(overlay);
  const abort=new AbortController(),options={signal:abort.signal};let finished=false,started=false,timer,frame;
  const setState=s=>hero.dataset.introState=s;
  const arm=ms=>{clearTimeout(timer);timer=setTimeout(()=>finish('failed'),ms)};
  function position(){const r=hero.getBoundingClientRect();for(const node of [video,shade])Object.assign(node.style,{left:r.left+'px',top:r.top+'px',width:r.width+'px',height:r.height+'px'});video.style.objectPosition=getComputedStyle(image).objectPosition;controls.style.bottom=Math.max(20,innerHeight-Math.min(innerHeight,r.bottom)+20)+'px'}
  function reveal(){document.querySelector('.header').inert=false;document.querySelector('.hero-content').inert=false;shade.style.opacity='1';document.body.classList.add('cinematic-revealing');overlay.classList.add('settled')}
  function tick(time){if(finished)return;if(time>=3.55)shade.style.opacity='1';if(time>=3.8){setState('transitioning');reveal()}}
  function frameTick(_,metadata){tick(metadata.mediaTime);if(!finished)frame=video.requestVideoFrameCallback(frameTick)}
  function finish(state='complete'){if(finished)return;finished=true;setState(state);clearTimeout(timer);abort.abort();if(frame!==undefined)video.cancelVideoFrameCallback?.(frame);video.pause();reveal();overlay.style.opacity='0';const focused=controls.contains(document.activeElement);setTimeout(()=>{overlay.remove();video.removeAttribute('src');video.load();document.body.classList.remove('cinematic-playing','cinematic-revealing');running=false;if(focused)(replay||document.querySelector('.hero-content .button'))?.focus({preventScroll:true})},340)}
  position();skip.addEventListener('click',()=>finish('skipped'),options);video.addEventListener('loadeddata',()=>setState('ready'),options);
  video.addEventListener('playing',()=>{if(!started){started=true;seen=sessionSeen=true;try{sessionStorage.setItem(storageKey,'seen')}catch{}setState('playing');overlay.style.opacity='1';document.body.classList.add('cinematic-playing');document.querySelector('.header').inert=true;document.querySelector('.hero-content').inert=true;skip.focus({preventScroll:true});if(video.requestVideoFrameCallback)frame=video.requestVideoFrameCallback(frameTick)}arm(8000)},options);
  video.addEventListener('timeupdate',()=>tick(video.currentTime),options);for(const name of ['waiting','stalled'])video.addEventListener(name,()=>arm(2500),options);
  video.addEventListener('ended',()=>finish(),options);video.addEventListener('error',()=>finish('failed'),options);
  document.addEventListener('keydown',e=>{if(e.key==='Escape')finish('skipped')},options);document.addEventListener('visibilitychange',()=>{if(document.hidden)finish('skipped')},options);
  const initialPortrait=mobile.matches;
  addEventListener('resize',()=>{if(mobile.matches!==initialPortrait)finish('skipped');else position()},options);addEventListener('scroll',()=>{if(hero.getBoundingClientRect().bottom<innerHeight*.35)finish('skipped');else position()},{...options,passive:true});addEventListener('pagehide',()=>finish('skipped'),options);reduce.addEventListener('change',()=>{if(reduce.matches)finish('skipped')},options);
  arm(8000);try{await video.play()}catch{finish('failed')}
 }
 replay?.addEventListener('click',()=>play(true));hero.dataset.introState='idle';await play();
}
