# Verification report

October 9, 2026.

Passed: 25 HTML routes and 24 sitemap entries; unique metadata/H1s; local links and responsive assets; eight services, seven cities, six projects and original FAQs. Nineteen Node tests pass, including cinematic eligibility, provider acceptance/rejection/activation, malformed requests, origin validation, hashed-IP durable SQL limits and Node handler validation. No real email was sent.

Desktop and mobile video codecs decode without errors. Both static hero images match the decoded MP4 final frame pixel for pixel. Logo transparency is present. Browser replay uses the correct mobile/desktop source, starts muted, allows sound without restarting and restores the page after Skip. Normal playback removes the video overlay. Session reload retains the static hero. Reduced-motion and connection eligibility were unit tested.

Previous responsive checks cover homepage, gallery and contact at 320, 375, 390, 430, 768, 1024, 1440 and 1920 pixels with no horizontal overflow. Mobile navigation, gallery filtering/dialog navigation/Escape and coverage map selection/reset were checked. The local Worker serves assets and the contact endpoint; provider delivery is mocked.

Owner dependencies: FormSubmit email activation and a real inbox delivery test; original logo artwork comparison; genuine before-and-after pairs and verified review content if desired. These were not fabricated. No field Core Web Vitals, Lighthouse score or full screen-reader audit is claimed. Kitchen imagery is illustrative, and cinematic water sound is procedural. Sites uses durable SQL limits; Vercel uses a per-instance fallback until a shared edge limiter is configured.

Gallery overhaul: see GALLERY-IMPLEMENTATION.md for the new browser checks, connected route tests, filters and focus restoration. Opening cinematic sound was removed following owner feedback. FFmpeg verifies that all four video files have no audio streams; final-frame pixel matches remain unchanged. The no-motion gallery control was tested; a real OS reduced-motion preference was not emulated.
# October 9 homepage and performance refinement

Build and all 19 existing tests pass. Syntax checks pass for site, gallery and cinematic modules. In-app Chromium browser checks: no horizontal overflow at 320, 390, 768 and 1440 pixels; mobile Commercial filter correctly yields two projects; the Water Station valve opens its matching dialog and closes with focus restored; desktop cinematic routing still initializes; no browser console errors observed.

Mobile generates zero physical-network paths and skips the gallery scroll animation entirely. Small gallery image assets total 430,094 bytes versus 1,128,666 bytes for originals (about 62% less); full images are requested when details open. This is a payload reduction, not a measured real-device load-time or frame-rate guarantee. Real Safari/iOS/Android and throttled production-network profiling were not available in this pass.

Published entrance uses static fallback because existing footage fails the new photorealism brief. Local draft playback remains available; final production video/audio have not been created. Native integration has been hardened but error/stall branches were code-reviewed, not exhaustively browser-injected. FormSubmit activation and live submissions were left untouched.
