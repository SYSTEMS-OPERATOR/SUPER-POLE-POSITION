import pytest
from super_pole_position.physics.track import Track


def test_load_namco_track():
    try:
        track = Track.load_namco("fuji_namco")
    except FileNotFoundError:
        pytest.skip("namco assets missing")
    assert track.width > 0 and track.height > 0
