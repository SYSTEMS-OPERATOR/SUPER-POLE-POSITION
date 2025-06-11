import pytest
ui = pytest.importorskip('super_pole_position.ui.arcade')

def test_available():
    assert isinstance(ui.available(), bool)
