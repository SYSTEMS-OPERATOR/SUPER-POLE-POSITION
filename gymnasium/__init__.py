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
    """Base space with minimal sampling interface."""

    def sample(self) -> np.ndarray:
        """Return a random element of the space."""
        raise NotImplementedError

class Box(Space):
    """Continuous space bounded by ``low`` and ``high``."""

    def __init__(self, low, high, shape=None, dtype=np.float32) -> None:
        self.low = np.array(low, dtype=dtype)
        self.high = np.array(high, dtype=dtype)
        self.shape = shape if shape is not None else self.low.shape
        self.dtype = dtype

    def sample(self) -> np.ndarray:
        """Return a random point within the box."""
        return np.random.uniform(self.low, self.high, self.shape).astype(self.dtype)

class Dict(Space):
    """Dictionary of named sub-spaces."""

    def __init__(self, spaces: dict) -> None:
        self.spaces = spaces

    def sample(self) -> dict:
        """Return a random element from each sub-space."""
        return {k: space.sample() for k, space in self.spaces.items()}

class spaces:
    Box = Box
    Dict = Dict
