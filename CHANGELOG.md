# 📜 Changelog

## Arcade Parity Improvements
- Adjust scanline intensity for stronger CRT-style effect.
- Adjust puddle traction slowdown to 0.65 for stickier puddles.
- Engine pitch factor configurable via `config.arcade_parity.yaml`; default increased for more authentic rev sound.
- Parameterized scanline effect intensity via `config.arcade_parity.yaml`.
- Reduced default scanline darkness for a softer CRT vibe.
- Lap times now sent to the scoreboard API at each lap and race end.
- Added `scoreboard-sync` command to mirror scores from a remote server.
