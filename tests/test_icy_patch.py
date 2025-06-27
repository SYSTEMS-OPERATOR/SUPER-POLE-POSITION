from super_pole_position.physics.car import Car
from super_pole_position.physics.track import Track, IcyPatch


def test_icy_patch_drift() -> None:
    patch = IcyPatch(x=10, y=10, radius=5, drift=0.2)
    track = Track(width=20, height=20, icy_patches=[patch])
    car = Car(x=10, y=10, speed=5.0)
    angle_before = car.angle
    car.apply_controls(False, False, 0.0, dt=1.0, track=track)
    assert car.angle != angle_before


def test_load_snow_track() -> None:
    track = Track.load("snow_mountain")
    assert track.icy_patches
