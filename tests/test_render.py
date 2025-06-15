import pytest  # noqa: F401

pygame = pytest.importorskip("pygame")
from super_pole_position.envs.pole_position import PolePositionEnv  # noqa: E402
from super_pole_position.ui.arcade import Pseudo3DRenderer  # noqa: E402


def test_dynamic_curve_perspective(monkeypatch):
    screen = pygame.Surface((320, 240))
    env = PolePositionEnv(render_mode="human")
    env.reset()
    renderer = Pseudo3DRenderer(screen)

    monkeypatch.setattr(env.track, "curvature_at", lambda s: 0.0)
    x1_zero, x2_zero, _ = renderer.draw_road(env)

    monkeypatch.setattr(env.track, "curvature_at", lambda s: 1.0)
    x1_curve, x2_curve, _ = renderer.draw_road(env)

    assert x1_curve > x1_zero
    assert x2_curve > x2_zero
