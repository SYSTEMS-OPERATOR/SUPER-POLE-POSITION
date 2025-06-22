import json
import pathlib

def test_fuji_json_loads():
    p = pathlib.Path("src/data/track_fuji.json")
    data = json.loads(p.read_text())
    assert isinstance(data, list)
    assert sum(seg["length"] for seg in data) in (4100, 4104)
