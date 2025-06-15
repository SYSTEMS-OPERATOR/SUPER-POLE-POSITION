import pytest  # noqa: F401
from super_pole_position.envs.pole_position import PolePositionEnv  # noqa: E402
from super_pole_position.ui.arcade import Pseudo3DRenderer  # noqa: E402

pygame = pytest.importorskip("pygame")


def test_perf_hud(monkeypatch):
    screen = pygame.Surface((320, 240))
    env = PolePositionEnv(render_mode="human")
    env.reset()
    env.latency_ms = 5
    env.loop_hz = 60
    renderer = Pseudo3DRenderer(screen)

    texts = []

    def fake_render(text, aa, color):
        texts.append(text)
        return pygame.Surface((1, 1))

    renderer.font.render = fake_render
    renderer.draw(env)
    assert any("LAG" in t for t in texts)
