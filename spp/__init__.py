"""Alias package forwarding to :mod:`super_pole_position`."""
from super_pole_position.__main__ import main
from super_pole_position.envs.pole_position import PolePositionEnv
import os


def make_env(**kwargs) -> PolePositionEnv:
    """Return a configured :class:`PolePositionEnv`."""

    render_mode = kwargs.pop("render_mode", "human")
    seed = kwargs.pop("seed", 0)
    if render_mode == "headless":
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    env = PolePositionEnv(render_mode=render_mode, **kwargs)
    env.reset(seed=seed)
    return env


__all__ = ["main", "make_env"]
