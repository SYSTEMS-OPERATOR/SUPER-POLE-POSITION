import hashlib
import pytest
from super_pole_position.envs.pole_position import PolePositionEnv


@pytest.mark.skip("golden hash unstable on CI")
def test_golden_obs_md5():
    env = PolePositionEnv(render_mode="human")
    obs, _ = env.reset(seed=42)
    bs = bytearray()
    while len(bs) < 10000:
        obs, _, done, _, _ = env.step({"throttle": False, "brake": False, "steer": 0})
        bs.extend(obs.tobytes())
        if done:
            break
    env.close()
    bs = bs[:10000]
    md5 = hashlib.md5(bs).hexdigest()
    with open("tests/baseline/golden_obs.md5") as f:
        expected = f.read().strip()
    assert md5 == expected
