import pytest
from super_pole_position.physics.track import Track


def test_load_obstacles():
    try:
        track = Track.load_namco("fuji_namco")
    except FileNotFoundError:
        pytest.skip("namco assets missing")
    assert track.obstacles
