import pytest
import spp

pygame = pytest.importorskip("pygame")


def test_player_sprite_visible():
    env = spp.make_env(render_mode="headless", seed=7)
    env.reset()
    for _ in range(30):
        obs, _, done, _, info = env.step(env.action_space.sample())
        if done:
            break
    surface = info["frame"]
    width, height = surface.get_size()
    sample = surface.get_at((width // 2, int(height * 0.9)))
    assert sample.r > 150 and sample.g < 50
    env.close()
