from super_pole_position.physics.track import Track


def test_load_obstacles():
    track = Track.load_namco("fuji_namco")
    assert track.obstacles
