# 🕹️ Arcade Parity Progress

## Design Objectives

- [x] Pseudo-3D track with a vanishing-point horizon that sways on curves
- [x] Raster display emulating the 256×224 resolution and broad color palette
- [x] Scrolling playfield built from scanline-aligned segments
- [x] Sprite scaling so cars and signboards grow smoothly when approaching
- [x] Full-color scenery and billboards that shrink toward the horizon

## Implemented Features

- [x] Authentic Fuji Speedway & additional circuits
- [x] Crash & explosion animations + sound
- [x] Billboards, guardrails & off-road hazards
- [x] Voice samples (“Get Ready!”, “Final Lap!”) & BGM
- [x] Full HUD: lap counter, timer, position, mini-map
- [x] Cabinet-style color palette & scanline effect
- [x] Test suite for each new feature
- [x] Stereo engine audio panned by car position
- [x] Minimal SFX manager with chiptune placeholders
- [x] Lap times posted to scoreboard API
- [x] Lap time leaderboard accessible via API
- [x] Player name recorded in high-score table
- [x] Grass-colored terrain and banked car sprites

🎉 All core arcade mechanics implemented! 🏁

## Upcoming Features

- [ ] Qualify-to-race transition with start position message
- [ ] Score bonus tiers for high qualifying ranks
- [ ] Difficulty options for time allowance per lap
- [ ] Expanded end-of-race sequence with rank display
- [ ] Local high-score entry and leaderboard screen
- [ ] Optional attract mode cycling the leaderboard
- [x] Finish-line check when timer hits exactly zero
- [x] Puddles placed at original track corners
