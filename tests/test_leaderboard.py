import json
from pathlib import Path

from super_pole_position.matchmaking.arena import update_leaderboard


def test_update_leaderboard(tmp_path: Path) -> None:
    file = tmp_path / "lb.json"
    update_leaderboard(file, "agent", 1.0)
    data = json.loads(file.read_text())
    assert data["results"][0]["name"] == "agent"
