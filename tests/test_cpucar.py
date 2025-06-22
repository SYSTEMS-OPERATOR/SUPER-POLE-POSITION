from super_pole_position.ai_cpu import CPUCar
from super_pole_position.physics.car import Car
from super_pole_position.physics.track import Track


def test_cpucar_blocking():
    track = Track(width=200.0, height=100.0)
    cpu = CPUCar(x=0.0, y=1.0)
    player = Car(x=-6.0, y=1.2, speed=5.0)
    assert cpu.blocking(player, track)
    player.y = 2.0
    assert not cpu.blocking(player, track)
