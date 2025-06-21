from super_pole_position.ai_cpu import CPUCar
from super_pole_position.physics.car import Car


def test_cpucar_blocking():
    cpu = CPUCar(x=0.0, y=1.0)
    player = Car(x=-6.0, y=1.2, speed=5.0)
    assert cpu.blocking(player)
    player.y = 2.0
    assert not cpu.blocking(player)
