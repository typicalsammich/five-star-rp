import fs from 'node:fs';
const p=JSON.parse(fs.readFileSync('package.json'));p.scripts['build:static']='node scripts/build.mjs';p.scripts.build='node scripts/build-sites.mjs';p.devDependencies.sharp='^0.34.5';fs.writeFileSync('package.json',JSON.stringify(p,null,2));
const v=JSON.parse(fs.readFileSync('vercel.json'));v.buildCommand='npm run build:static';fs.writeFileSync('vercel.json',JSON.stringify(v,null,2));
let source=fs.readFileSync('scripts/build.mjs','utf8');source=source.replaceAll('${origin}/assets/hero-desktop.webp','${origin}/assets/social-card.png');fs.writeFileSync('scripts/build.mjs',source);
