# Rendered entrance v4

`render_entrance.py` creates a single 3D world with a copper supply, an open T junction and vertical riser, a hollow stainless gooseneck faucet, and a complete modeled kitchen. The camera follows the pipe, emerges from the outlet, rotates and pulls back. It stops at 3.8 seconds and holds through 4.5 seconds. There is no kitchen backplate, image zoom or crossfade to unrelated imagery in this version.

This is authored CGI. Water uses refractive materials, procedural surface displacement, a falling droplet/ripple and a modeled stream, rather than a fluid solver. It should not be described as filmed footage or a verified professional commercial production. The original commercial-quality aspiration remains a subjective visual target.

CPU rendering uses Cycles, denoising, 12 samples for the internal pipe, 16 for kitchen motion and 32 for the stopped kitchen frame. Desktop source frames are 960 x 540; portrait kitchen source frames are 540 x 765. Interior portrait frames use a centered aperture of the desktop renders because their camera route is identical. The portrait kitchen camera is separately composed around the sink and faucet. Frames are sampled at 15 fps and interpolated offline with FFmpeg optical flow to 30 fps. Delivery files are 1280 x 720 and 720 x 1020, 135 frames each. These are practical web assets, not native 1920 x 1080 or 60 fps masters.

`encode_entrance.mjs` produces H.264 MP4 with faststart and VP9 WebM. Each hero is extracted losslessly from decoded MP4 frame 134. `verify-media.mjs` checks raw pixel equality between that frame and the hero and fully decodes both delivery codecs. The native player selects MP4 for broad browser compatibility and uses the same object-fit/object-position as the hero.

Sound remains removed as requested. No procedural soundtrack or new audio recording is included. Silent playback enables policy-compatible autoplay; if playback is blocked, the decoded static hero remains available.

The player includes loading/ready/playing/transitioning/complete/skipped/failed states, decoded-hero readiness, video-frame timing with timeupdate fallback, versioned per-session eligibility, blocked-play/error/stall recovery, reduced-motion/data-saver/slow-connection handling and development-only replay. Lifecycle tests cover successful cleanup, skip, rejected play, stalls, storage denial, seen sessions, reduced motion and hero decode failure. Browser and media validation are recorded in TESTING.md; no unavailable device is claimed as tested.

Regenerate using Blender 4.5 with `-b -t 4 -P cinematic-production/render_entrance.py -- PROJECT_ROOT`, then repeat with environment `ENTRANCE_SIZE=mobile`. Render frames are resumable. Run `node cinematic-production/encode_entrance.mjs`, `node scripts/verify-media.mjs`, then the normal build and tests. Old `render_pipe.py` and `encode.mjs` preserve the earlier draft; they are not the current delivery pipeline.
