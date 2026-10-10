import fs from 'node:fs';import path from 'node:path';import {spawnSync} from 'node:child_process';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);let sharp;try{sharp=require('sharp')}catch{sharp=require('../../prosurface/node_modules/sharp')}
const root=path.resolve('.');const ffmpeg=process.env.FFMPEG_PATH||path.resolve('../imperial-crown/node_modules/ffmpeg-static/ffmpeg.exe');const output=path.resolve('public/assets/cinematic');const work=path.resolve('cinematic-production/frames/assembled');fs.mkdirSync(output,{recursive:true});fs.mkdirSync(work,{recursive:true});
for(const size of ['desktop','mobile']){let approved=`cinematic-production/approved-hero-${size}.webp`;if(!fs.existsSync(approved))fs.copyFileSync(`public/assets/hero-${size}.webp`,approved)}
function run(args){const r=spawnSync(ffmpeg,['-hide_banner','-loglevel','error','-y',...args],{stdio:'inherit'});if(r.status!==0)throw new Error('FFmpeg failed with '+r.status)}
const pipe='cinematic-production/frames/pipe-v2/%04d.png';for(let i=0;i<90;i++)if(!fs.existsSync(pipe.replace('%04d',String(i).padStart(4,'0'))))throw new Error('Missing Blender frame '+i);
for(const [size,width,height]of [['desktop',1280,720],['mobile',720,1020]]){
    const pipeMaster=path.join(work,`pipe-${size}.mp4`);const kitchenMaster=path.join(work,`kitchen-${size}.mp4`);const master=path.join(work,`${size}-master.mp4`);
    run(['-framerate','30','-i',pipe,'-vf',`scale=${width}:${height}:force_original_aspect_ratio=increase,crop=${width}:${height},setsar=1,fade=t=in:st=0:d=0.40`,'-frames:v','90','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p',pipeMaster]);
    const zoom="1+1.6*pow(max(0,1-on/32),3)";
    run(['-loop','1','-i',`cinematic-production/approved-hero-${size}.webp`,'-vf',`scale=2560:-1,zoompan=z='${zoom}':x='(iw-iw/zoom)*0.98':y='(ih-ih/zoom)*0.42':d=1:s=${width}x${height}:fps=30,setsar=1`,'-frames:v','54','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p',kitchenMaster]);
    run(['-i',pipeMaster,'-i',kitchenMaster,'-filter_complex','[0:v]settb=AVTB[p];[1:v]settb=AVTB[k];[p][k]xfade=transition=fade:duration=0.25:offset=2.75,format=yuv420p[v]','-map','[v]','-frames:v','135','-t','4.5','-c:v','libx264','-preset','slow','-crf','19','-an','-movflags','+faststart',master]);
    const mp4=path.join(output,`plumbing-intro-${size}.mp4`);fs.copyFileSync(master,mp4);
    run(['-i',mp4,'-c:v','libvpx-vp9','-crf','30','-b:v','0','-row-mt','1','-an',path.join(output,`plumbing-intro-${size}.webm`)]);
    const final=path.join(work,`${size}-final.png`);run(['-i',mp4,'-vf','select=eq(n\\,134)','-frames:v','1',final]);
    await sharp(final).webp({lossless:true}).toFile(`public/assets/hero-${size}.webp`);
    const poster=path.join(work,`${size}-poster.png`);run(['-i',mp4,'-vf','select=eq(n\\,4)','-frames:v','1',poster]);await sharp(poster).webp({quality:90}).toFile(path.join(output,`plumbing-intro-poster-${size}.webp`));
    console.log('Encoded',size,width,height,'135 frames / 4.5 seconds. Hero exported from decoded final frame.');
}
fs.writeFileSync('public/cinematic.json',JSON.stringify({desktop:{mp4:'/assets/cinematic/plumbing-intro-desktop.mp4',webm:'/assets/cinematic/plumbing-intro-desktop.webm',poster:'/assets/cinematic/plumbing-intro-poster-desktop.webp'},mobile:{mp4:'/assets/cinematic/plumbing-intro-mobile.mp4',webm:'/assets/cinematic/plumbing-intro-mobile.webm',poster:'/assets/cinematic/plumbing-intro-poster-mobile.webp'},productionReady:false,audio:null,audioTrack:'none',duration:4.5,status:'Offline Blender pipe footage, approved kitchen backplate and composited pullback, silent opening cinematic.'},null,2));
