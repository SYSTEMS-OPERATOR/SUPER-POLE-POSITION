from .car import Car

class TrafficCar(Car):
    """Simple AI car that follows a constant speed profile."""
    def __init__(self, x=0.0, y=0.0, target_speed=5.0):
        super().__init__(x=x, y=y)
        self.target_speed = target_speed

    def policy(self):
        """Return throttle/brake to reach target speed."""
        throttle = self.speed < self.target_speed
        brake = self.speed > self.target_speed
        return throttle, brake
