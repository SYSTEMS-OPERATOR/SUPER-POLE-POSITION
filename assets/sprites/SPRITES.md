# Sprite Assets

This file lists sprite names that the engine expects. Each PNG is a zero-byte
stub so no binary data ships with the repository. Use these filenames when
generating sprites programmatically.

- `player_car.png` – rear-view Formula 1 car. Size 32×32. Color hints: red body,
  white cockpit.
- `player_car_bankL.png` – banked left frame, 64×64.
- `player_car_bankR.png` – banked right frame, 64×64.
- `cpu_car.png` – other racers. Also 32×32. Provide both front and rear
  perspectives for overtaking scenes.
- `billboard_*.png` – eight road-side sign boards, each 32×32. These can share a
  palette but display different logos.
- `explosion_16f.png` – sprite sheet with 16 frames, each frame 32×32. Use this
  for the crash animation.
- `mt_fuji.png` – wide background of Mount Fuji. Target width ~256, height 64.
- `clouds.png` – parallax layer for the sky, width 256, height ~32.

All files are empty placeholders. Replace them with generated pixel art at build
time.
