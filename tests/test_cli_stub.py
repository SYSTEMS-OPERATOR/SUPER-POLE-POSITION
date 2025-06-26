import os
import subprocess
import sys
import pytest


@pytest.mark.skipif(not os.getenv("CI_SLOW_TESTS"), reason="slow test")
def test_cli_stub() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "spp", "--headless", "--steps", "3"],
        timeout=5,
    )
    assert result.returncode == 0
