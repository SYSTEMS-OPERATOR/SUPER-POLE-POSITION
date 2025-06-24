# Sprite Requirements

The following items capture sprite-related work from the **Top 10 Graphic-Fidelity Tasks** list.

## Authentic Car Sprites
- Replace placeholder images with pixel-perfect redraws of the original Namco rear-view cars.
- Include banking frames at ±10° and switch sprites when steering exceeds 0.3.
- Match the arcade palette (bright red chassis, dark tyres, grey rear wing).

## Opponent Car Variety
- Render every rival car visible within the camera frustum, sorted back-to-front.
- Use distinct color palettes — blue, yellow and white — as in the arcade ROM.

## Explosion Animation
- Recreate the four-phase explosion with a 16×64 px sprite sheet.
- Spawn separate wheel sprites that arc outward for roughly 0.6 s before fading.
- Flash the screen white briefly on the first frame for extra impact.
