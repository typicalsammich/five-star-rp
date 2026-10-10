# Five Star RP

25 indexable routes with a rendered cinematic, authentic gallery and interactive map. Use Node 22+: npm install, npm run build, npm run dev, npm test, npm run lint. Local preview: http://127.0.0.1:3015. npm run typecheck checks centralized content.

Vercel uses vercel.json, dist and api/contact.js. Set SITE_URL to the final origin before building; the default is https://fivestar-rp.com. Sites uses npm run build:sites, the Worker, an ASSETS binding and the DB migration in drizzle/.

FormSubmit targets fivestar-rp25@outlook.com. The owner must activate the address before relying on delivery. No submission or activation email was sent during development. Provider responses were tested with mocks. Acceptance means accepted for processing, not verified inbox delivery. CONTACT_WEBHOOK_URL and optional CONTACT_WEBHOOK_TOKEN can override the provider. Never commit secrets.

Sites uses durable SQL limits of five requests per ten minutes, hashed client addresses, server validation and a honeypot. Vercel uses a per-instance limiter; configure a shared edge limiter for multiple instances.

The 4.5-second desktop/mobile MP4 and WebM videos are silent. public/cinematic.js supports versioned first-session-only muted playback, skip, development-only replay, reduced-motion and slow-connection fallback. Static hero images are exported from each decoded final MP4 frame.

The entrance is offline Blender Cycles CGI: copper macro and droplet, open T junction, vertical riser, hollow stainless faucet, then a camera pullback into a modeled kitchen. The final view holds from 3.8 seconds. It is illustrative rendered imagery, not filmed company work or a physically simulated fluid solution. See docs/CINEMATIC-FINAL-ASSET-BRIEF.md for production settings and limits.

Centralized content preserves eight services, seven cities, six authentic projects and six original FAQs. No ratings, testimonials, project locations or before-and-after pairs were invented. The reveal component awaits genuine matching photos. The extracted logo has genuine alpha; compare with original artwork when available. Leaflet retains OpenStreetMap attribution and a city-list fallback. See data/source-manifest.json and docs/TESTING.md.

The desktop gallery is a connected SVG drafting world with cylindrical copper shading, rounded elbows, collars, branches and mechanical valves. Native desktop scroll drives camera transforms and reversible flow. Mobile uses a stationary CSS connection line with normal scrolling and no SVG route animation. Browse without motion presents the same desktop photos without cinematic effects. Real photos retain their source aspect ratios. See docs/GALLERY-IMPLEMENTATION.md.
