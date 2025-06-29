# 📜 Changelog

## v1.0.0-rc1
- First release candidate with `--2600-mode` for deterministic traffic.
- Golden observation hash locked in for CI.

## Arcade Parity Improvements
- Adjust scanline intensity for stronger CRT-style effect.
- Adjust puddle traction slowdown to 0.65 for stickier puddles.
- Engine pitch factor configurable via `config.arcade_parity.yaml`; default increased for more authentic rev sound.
- Parameterized scanline effect intensity via `config.arcade_parity.yaml`.
- Reduced default scanline darkness for a softer CRT vibe.
- Lap times now sent to the scoreboard API at each lap and race end.
- Lap time leaderboard endpoints added to the scoreboard API.
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
- Stereo engine audio now pans per player with `engine_pan_spread` and mixes
  alongside skid and crash effects.
- Added `JoystickAgent` for analog wheel and gamepad control.
- Steering sensitivity now configurable via `turn_rate` in
  `config.arcade_parity.yaml` with optional brake disable using
  `DISABLE_BRAKE`.
- Off-track ground now renders in green with leaning car sprites.
- Difficulty setting added with expert mode shortening time limits.
- Documented upcoming arcade-parity tasks in `PROGRESS_ARCADE_PARITY.md` and
  added roadmap items for qualify-to-race and high-score table.

- Fixed duplicate menu tick sound load for gear shifts.
📌 Keep racing for the next update! 🏁

