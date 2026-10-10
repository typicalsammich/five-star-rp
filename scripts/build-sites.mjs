import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {execFileSync} from 'node:child_process';
const require=createRequire(import.meta.url);let esbuild;try{esbuild=require('esbuild')}catch{esbuild=require('../../prosurface/node_modules/esbuild')}
execFileSync(process.execPath,['scripts/build.mjs'],{stdio:'inherit'});
const dist=path.resolve('dist');const client=path.join(dist,'client');fs.mkdirSync(client,{recursive:true});
for(const entry of fs.readdirSync(dist))if(!['client','server','.openai','_appgen_meta'].includes(entry))fs.cpSync(path.join(dist,entry),path.join(client,entry),{recursive:true});
await esbuild.build({entryPoints:['worker/index.mjs'],bundle:true,format:'esm',platform:'browser',target:'es2022',outfile:'dist/server/index.js',minify:true});
const manifest=JSON.parse(fs.readFileSync('.openai/hosting.json','utf8'));if(manifest.static)throw new Error('Sites Worker build must not declare static hosting.');
fs.mkdirSync('dist/.openai',{recursive:true});fs.writeFileSync('dist/.openai/hosting.json',JSON.stringify(manifest,null,2));fs.cpSync('drizzle','dist/.openai/drizzle',{recursive:true});
fs.writeFileSync('dist/server/wrangler.json',JSON.stringify({name:'five-star-rp',main:'index.js',compatibility_date:'2026-05-22',assets:{directory:'../client',binding:'ASSETS',run_worker_first:['/api/*']},d1_databases:[{binding:'DB',database_name:'site-creator-d1',database_id:'00000000-0000-4000-8000-000000000000'}]},null,2));
console.log('Sites Worker packaged with assets and durable contact rate limits.');
