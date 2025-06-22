import json
import os
import types
import pygame

pygame = pygame  # ensure import before pytest skip
from super_pole_position.ui.arcade import ArcadeRenderer
from super_pole_position.evaluation import scores


def test_scoreboard_overlay(tmp_path):
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((160, 120))

    scoreboard = tmp_path / "scores.json"
    scoreboard.write_text(json.dumps({"scores": [{"name": "AAA", "score": 500}]}))
    os.environ["SPP_SCORES"] = str(scoreboard)
    os.environ["AUDIO"] = "0"

    renderer = ArcadeRenderer(screen)
    dummy_sound = types.SimpleNamespace(play=lambda *a, **k: None)
    renderer.engine_sound = dummy_sound
    renderer.skid_sound = dummy_sound
    renderer.crash_sound = dummy_sound
    renderer.channels = [
        types.SimpleNamespace(play=lambda *a, **k: None, get_busy=lambda: False)
        for _ in range(3)
    ]
    env = types.SimpleNamespace(
        cars=[types.SimpleNamespace(x=0.0, y=0.0, speed=0.0, gear=0)],
        track=types.SimpleNamespace(angle_at=lambda x: 0.0, width=160, height=120, progress=lambda c: 0.0),
        start_phase="",
        current_step=60,
        message_timer=1.0,
        game_message="FINISHED!",
        remaining_time=0.0,
        lap_timer=0.0,
        last_lap_time=None,
        lap_flash=0.0,
        time_extend_flash=0.0,
        lap=0,
        score=100,
        high_score=100,
        crash_timer=0.0,
    )
    renderer.draw(env)
    color = screen.get_at((80, 80))[:3]
    assert color != (0, 0, 0)
    pygame.display.quit()
