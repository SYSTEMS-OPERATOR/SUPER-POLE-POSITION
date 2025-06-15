import pathlib

from super_pole_position.ui.arcade import SCANLINE_ALPHA


def test_scanline_intensity_improved():
    baseline_path = pathlib.Path(__file__).with_name("baseline_scanline.txt")
    baseline_alpha = int(baseline_path.read_text().strip())
    assert SCANLINE_ALPHA >= baseline_alpha + 5
