import fs from 'node:fs';import path from 'node:path';import {spawnSync} from 'node:child_process';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);let sharp;try{sharp=require('sharp')}catch{sharp=require('../../prosurface/node_modules/sharp')}
const ffmpeg=path.resolve('../imperial-crown/node_modules/ffmpeg-static/ffmpeg.exe'),work=path.resolve('cinematic-production/frames/encoded-v4'),out=path.resolve('public/assets/cinematic');fs.mkdirSync(work,{recursive:true});
function run(args){const r=spawnSync(ffmpeg,['-hide_banner','-loglevel','error','-y',...args],{stdio:'inherit'});if(r.status!==0)throw new Error('Media conversion failed')}
// Inside the pipe both cameras follow the same center line. Derive the portrait
// aperture there; the separately rendered portrait camera takes over at the exit.
for(let f=0;f<47;f++){const name=String(f).padStart(4,'0')+'.png',source=path.resolve('cinematic-production/frames/entrance-v4/desktop',name),target=path.resolve('cinematic-production/frames/entrance-v4/mobile',name);const meta=await sharp(source).metadata();const width=Math.round(meta.height*540/765);await sharp(source).extract({left:Math.floor((meta.width-width)/2),top:0,width,height:meta.height}).resize(540,765).png().toFile(target)}
for(const [size,w,h]of [['desktop',1280,720],['mobile',720,1020]]){
 const folder=path.resolve('cinematic-production/frames/entrance-v4',size);for(let f=0;f<70;f++){const file=path.join(folder,String(f).padStart(4,'0')+'.png');if(!fs.existsSync(file))throw new Error('Missing '+size+' frame '+f);await sharp(file).stats()}
 const mp4=path.join(out,`flow-entrance-${size}-v4.mp4`),webm=path.join(out,`flow-entrance-${size}-v4.webm`);
 // Offline optical-flow interpolation produces a 30 fps delivery from 15 fps ray-traced frames.
 run(['-framerate','15','-i',path.join(folder,'%04d.png'),'-vf',`minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=${w}:${h}:flags=lanczos,eq=gamma='1+0.65*max(0,min(1,(t-1.5)/0.3))*max(0,min(1,(3.1-t)/0.3))':eval=frame,fade=t=in:st=0:d=0.22,setsar=1`,'-frames:v','135','-t','4.5','-an','-c:v','libx264','-crf','20','-preset','slow','-pix_fmt','yuv420p','-movflags','+faststart',mp4]);
 run(['-i',mp4,'-an','-c:v','libvpx-vp9','-crf','32','-b:v','0','-row-mt','1',webm]);
 const final=path.join(work,size+'-final.png');run(['-i',mp4,'-vf','select=eq(n\\,134)','-frames:v','1',final]);await sharp(final).webp({lossless:true}).toFile(`public/assets/hero-${size}.webp`);
 const poster=path.join(work,size+'-poster.png');run(['-i',mp4,'-vf','select=eq(n\\,2)','-frames:v','1',poster]);await sharp(poster).webp({quality:88}).toFile(path.join(out,`flow-entrance-${size}-poster-v4.webp`));console.log('Encoded and derived matching hero:',size);
}
const media=size=>({mp4:`/assets/cinematic/flow-entrance-${size}-v4.mp4`,webm:`/assets/cinematic/flow-entrance-${size}-v4.webm`,poster:`/assets/cinematic/flow-entrance-${size}-poster-v4.webp`});
fs.writeFileSync('public/cinematic.json',JSON.stringify({version:'faucet-kitchen-v4',desktop:media('desktop'),mobile:media('mobile'),productionReady:true,audio:null,audioTrack:'none',duration:4.5,status:'Silent offline Cycles CGI: copper supply, vertical riser, modeled faucet outlet and 3D kitchen pullback. 30 fps delivery, optical-flow interpolation, final-frame heroes.'},null,2)+'\n');
