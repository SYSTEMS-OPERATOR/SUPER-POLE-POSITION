from super_pole_position.envs.pole_position import engine_pitch
from pathlib import Path


def test_engine_pitch_improved():
    baseline_path = Path('benchmarks/baseline_engine_pitch.txt')
    baseline_val = float(baseline_path.read_text().split('=')[1])
    new_val = engine_pitch(0.5)
    assert new_val - baseline_val >= 49.9
