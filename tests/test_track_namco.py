from super_pole_position.physics.track import Track


def test_load_namco_track():
    track = Track.load_namco("fuji_namco")
    assert track.width > 0 and track.height > 0
