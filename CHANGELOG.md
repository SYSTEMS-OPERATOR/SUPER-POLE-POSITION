# 📜 Changelog

## Arcade Parity Improvements
- Adjust scanline intensity for stronger CRT-style effect.
- Adjust puddle traction slowdown to 0.65 for stickier puddles.
- Engine pitch factor configurable via `config.arcade_parity.yaml`; default increased for more authentic rev sound.
- Parameterized scanline effect intensity via `config.arcade_parity.yaml`.
- Reduced default scanline darkness for a softer CRT vibe.
- Lap times now sent to the scoreboard API at each lap and race end.
- Added `audio_volume` setting in `config.py` controlling pygame mixer volume.
- Added `scoreboard-sync` command to mirror scores from a remote server.
- Introduced `TrackCurve` helper and new `fuji_curve` track data.
- Added `--mute-bgm` CLI flag to disable background music.
- Added `CPUCar` AI with blocking behaviour and `Track.is_on_road` helper.
- Added placeholder sprite and audio asset directories.
- Placeholder sprite and audio files are now committed as zero-byte stubs.
- Added `load_sprite` helper to load PNGs when available with ASCII fallback.
- Engine pitch now factors in current gear for smoother shifts.
- Added on-screen high-score display and `examples/reset_high_scores.py` utility.

📌 Keep racing for the next update! 🏁

