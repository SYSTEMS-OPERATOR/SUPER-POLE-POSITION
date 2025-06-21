from super_pole_position.physics.track import Track


def test_is_on_road_basic():
    track = Track(width=10.0, height=2.0, road_width=2.0)
    assert track.is_on_road(5.0, 1.0)
    assert not track.is_on_road(5.0, 2.1)
