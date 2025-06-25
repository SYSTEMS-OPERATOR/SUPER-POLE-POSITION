import numpy as np

class Env:
    """Minimal Gymnasium-like environment base class supporting seeding."""

    metadata: dict = {}
    action_space = None
    observation_space = None

    def __init__(self) -> None:  # pragma: no cover - minimal init
        self.np_random = np.random.default_rng()

    def step(self, action):  # pragma: no cover - abstract stub
        raise NotImplementedError

    def reset(self, *, seed=None, options=None):  # pragma: no cover - seed only
        if seed is not None:
            self.np_random = np.random.default_rng(seed)

    def render(self):
        pass

    def close(self):
        pass

class Space:
    pass

class Box(Space):
    def __init__(self, low, high, shape=None, dtype=np.float32):
        self.low = np.array(low, dtype=dtype)
        self.high = np.array(high, dtype=dtype)
        self.shape = shape if shape is not None else self.low.shape
        self.dtype = dtype

class Dict(Space):
    def __init__(self, spaces: dict):
        self.spaces = spaces

class spaces:
    Box = Box
    Dict = Dict
