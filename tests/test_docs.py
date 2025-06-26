from pathlib import Path


def test_readme_instructions():
    readme = Path("README.md").read_text()
    assert "pip install super-pole-position" in readme
    assert "pole-position --headless --steps 120 --seed 42" in readme
