import os
import subprocess
import sys
from pathlib import Path

from aria import hello


def test_hello():
    assert hello() == "Hello, Aria!"


def test_python_m_aria_runs_help():
    project_root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(project_root / "src"), environment.get("PYTHONPATH", "")]
    )
    result = subprocess.run(
        [sys.executable, "-m", "aria", "--help"],
        capture_output=True,
        text=True,
        cwd=project_root,
        env=environment,
    )
    assert result.returncode == 0
    assert "ARIA autonomous trading runtime" in result.stdout


def test_python_m_aria_rejects_non_positive_capital():
    project_root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(project_root / "src"), environment.get("PYTHONPATH", "")]
    )
    result = subprocess.run(
        [sys.executable, "-m", "aria", "--capital", "-100"],
        capture_output=True,
        text=True,
        cwd=project_root,
        env=environment,
    )

    assert result.returncode == 2
    assert "capital must be positive" in result.stderr
