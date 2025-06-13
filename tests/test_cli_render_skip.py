import sys
import pytest
from super_pole_position import cli


def test_cli_render_skip(monkeypatch):
    monkeypatch.setitem(sys.modules, "pygame", None)
    monkeypatch.setattr(sys, "argv", ["spp", "race", "--render"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1
