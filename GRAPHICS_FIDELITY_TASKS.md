# Graphic Fidelity Tasks

The following tasks outline key areas to reach an arcade-perfect presentation for the Fuji Speedway circuit in **Pole Position (1982)**.

| # | Area | Description | Suggestions |
|---|------|-------------|-------------|
|1|Authentic Car Sprites|Placeholder sprites lack banking frames.|Replace `player_car.png` and `cpu_car_*.png` with redraws of the arcade sprites. Switch to banked frames when steering magnitude exceeds 0.3.|
|2|Opponent Car Variety|Only one rival sprite is shown.|Draw all visible traffic cars and use palettes matching the original blue, yellow and white liveries.|
|3|Explosion Animation|Current effect is generic.|Implement the four-phase fireball with wheel debris and a quick white screen flash.|
|4|Red-and-White Road Shoulders|Stripe spacing and thickness are off.|Increase vertical resolution to 48–64 slices and use a 4 px red/4 px white pattern that scrolls with the road.|
|5|Grass & Off-Track Color|Ground appears grey.|Apply arcade grass tone `#007000` with a subtle vertical gradient.|
|6|Mount Fuji & Cloud Parallax|Horizon elements feel static.|Add dual-layer clouds moving at different speeds and offset Mount Fuji ±4 px with steering.|
|7|Billboard Artwork & Scaling|Placeholders and scale snapping.|Trace the original billboard art, precompute scale levels and add a faint ground shadow.|
|8|Start/Finish Gantry|No gantry sprites.|Introduce a "FUJI START" banner with countdown lights that change from red to green.|
|9|CRT/Scanline Filter|Only a single overlay.|Render off-screen at 512×448, apply barrel distortion, an RGB mask and light scanlines, then downscale with nearest neighbor.|
|10|HUD Font & Palette|Generic fonts and colors.|Use the ROM-derived bitmap font and original nine-color palette. Flash the timer red at 4 Hz when time is under 10 s.|

