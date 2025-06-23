import sys
from super_pole_position.ui import menu


def test_show_race_outro_fallback(capsys, monkeypatch):
    monkeypatch.setattr(menu, "pygame", None)
    monkeypatch.setattr(menu.score_mod, "load_scores", lambda *_: [{"name": "AAA", "score": 50}])
    menu.show_race_outro(None, 42, duration=0)
    out = capsys.readouterr().out
    assert "FINAL SCORE 42" in out
    assert "AAA" in out

