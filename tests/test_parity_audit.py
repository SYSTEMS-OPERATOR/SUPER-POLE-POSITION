import json
import os
import subprocess
import sys
from pathlib import Path


def test_parity_audit_runs(tmp_path: Path) -> None:
    out = tmp_path / "parity.json"
    result = subprocess.run(
        [sys.executable, "tools/parity_audit.py", "--dump", str(out), "--frames", "5"],
        env={**os.environ, "FAST_TEST": "1", "SDL_VIDEODRIVER": "dummy"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
    )
    assert result.returncode == 0
    data = json.loads(out.read_text())
    assert {"physics_delta", "render_similarity", "audio_similarity"} <= set(data)
