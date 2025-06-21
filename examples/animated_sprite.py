from __future__ import annotations

"""Simple animated sprite movement demo using Pygame 2."""

from dataclasses import dataclass
from typing import List

import pygame

WIDTH, HEIGHT = 256, 224
FPS = 60
FRAME_DURATION = 0.15


@dataclass
class Player:
    """Represent the controllable character."""

    pos: pygame.Vector2
    frames: List[pygame.Surface]
    index: int = 0
    timer: float = 0.0

    def update(self, dt: float) -> None:
        """Advance animation frames."""
        self.timer += dt
        if self.timer >= FRAME_DURATION:
            self.timer -= FRAME_DURATION
            self.index = (self.index + 1) % len(self.frames)

    @property
    def image(self) -> pygame.Surface:
        """Return the current frame image."""
        return self.frames[self.index]

    def draw(self, surface: pygame.Surface) -> None:
        """Blit the current frame to ``surface``."""
        rect = self.image.get_rect(center=self.pos)
        surface.blit(self.image, rect)


def load_frames() -> List[pygame.Surface]:
    """Create placeholder frames with different colors."""
    colors = [(200, 50, 50), (50, 200, 50), (50, 50, 200), (200, 200, 50)]
    frames = []
    for color in colors:
        frame = pygame.Surface((32, 32))
        frame.fill(color)
        pygame.draw.rect(frame, (255, 255, 255), frame.get_rect(), 2)
        frames.append(frame.convert())
    return frames


def main() -> None:
    """Run the demo."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Animated Sprite Demo")
    clock = pygame.time.Clock()

    player = Player(pos=pygame.Vector2(WIDTH / 2, HEIGHT / 2), frames=load_frames())
    speed = 120

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.pos.x -= speed * dt
        if keys[pygame.K_RIGHT]:
            player.pos.x += speed * dt
        if keys[pygame.K_UP]:
            player.pos.y -= speed * dt
        if keys[pygame.K_DOWN]:
            player.pos.y += speed * dt

        player.update(dt)

        screen.fill((0, 0, 0))
        player.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
