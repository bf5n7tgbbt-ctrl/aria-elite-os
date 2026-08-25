import subprocess
import sys

from aria import hello


def test_hello():
    assert hello() == "Hello, Aria!"


def test_python_m_aria_runs_help():
    result = subprocess.run(
        [sys.executable, "-m", "aria", "--help"],
        capture_output=True,
        text=True,
        cwd="/workspaces/aria-elite-os",
    )
    assert result.returncode == 0
    assert "ARIA autonomous trading runtime" in result.stdout
