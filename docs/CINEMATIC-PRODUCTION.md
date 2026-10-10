# Inside the Flow production

Delivered October 9, 2026: 1280x720 desktop and 720x1020 mobile, 135 frames at 30 fps. MP4/H.264/AAC and WebM/VP9/Opus. Original procedural droplets, water movement, copper resonance and pipe rumble; no music or narration.

Opening footage is offline Blender 4.5.14 LTS Cycles, 960x540, eight denoised samples. Reflective copper geometry, shallow rippled water, condensation, a droplet and a banked T-junction camera path lead to an architectural backplate. A composited pullback resolves into the approved kitchen. This is not a fluid-volume simulation or fully modeled kitchen.

Timing: fade in 0-.4; impact .44; acceleration .5-1.5; junction 1.5-2.3; exit 2.3-3; kitchen pullback 2.75-3.82; resolved image through 4.5. Text appears at 3.8. Hero WebPs are lossless exports of decoded MP4 frame 134.

Reproduction: install official Blender 4.5 LTS, FFmpeg and sharp. Run Blender in background with -P cinematic-production/render_pipe.py -- ABSOLUTE_PROJECT_PATH. Existing frames are skipped. CINEMATIC_SAMPLES controls render quality. Run python cinematic-production/sound_design.py, then node cinematic-production/encode.mjs with FFMPEG_PATH set. Approved input WebPs are preserved to avoid cumulative recompression. The encoder has fallbacks for this workspace's installed tools; a fresh environment needs sharp and FFMPEG_PATH.

Blender official mirror: https://mirror.blender.org/release/Blender4.5/blender-4.5.14-windows-x64.zip. Binary tools and working frames are excluded from delivery. Public video, audio, posters, approved images, scripts and the Blender scene are included.

Update: the opening is now silent. All four distributed videos were remuxed without audio; the player has no sound control. Original experimental foley is archived under research/retired-audio and is not served. The encoder now produces silent output.
