from pathlib import Path


def test_readme_instructions():
    readme = Path("README.md").read_text()
    assert "pip install -r requirements.txt && python run_game.py" in readme
