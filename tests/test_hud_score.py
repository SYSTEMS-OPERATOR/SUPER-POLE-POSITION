import pytest  # noqa: F401
from super_pole_position.envs.pole_position import PolePositionEnv  # noqa: E402
from super_pole_position.ui.arcade import ArcadeRenderer  # noqa: E402

pygame = pytest.importorskip("pygame")


def test_score_hiscore_update(monkeypatch):
    screen = pygame.Surface((320, 240))
    env = PolePositionEnv(render_mode="human")
    env.reset()
    env.high_score = 200
    env.score = 100
    renderer = ArcadeRenderer(screen)

    texts = []

    def fake_render(text, aa, color):
        texts.append(text)
        return pygame.Surface((1, 1))

    renderer.font.render = fake_render
    renderer.draw(env)
    assert env.high_score == 200
    env.score = 250
    renderer.draw(env)
    assert env.high_score == 250
    assert any("HI" in t for t in texts)
