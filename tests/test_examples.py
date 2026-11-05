"""Run installed-package examples in fresh Python processes, without keys on disk."""

from pathlib import Path
import os
import subprocess
import sys

import pytest


@pytest.mark.parametrize("filename,expected", [
    ("01_demo_de_hieu.py", "THÔNG ĐIỆP M = 30"),
    ("02_demo_rsa_2048.py", "Thông điệp dài 180 byte"),
    ("03_demo_oaep.py", "Cả ba người nhận có giải mã được không: True"),
    ("04_attack_lab.py", "Eve thu 3 bản mã"),
    ("05_conditions_analyzer.py", "Attack Conditions Analyzer"),
])
def test_demo_runs_with_installed_package(filename: str, expected: str, tmp_path: Path) -> None:
    script = Path(__file__).resolve().parents[1] / "examples" / filename
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONUTF8"] = "1"
    result = subprocess.run(
        [sys.executable, str(script)], cwd=tmp_path, env=environment,
        capture_output=True, text=True, encoding="utf-8", timeout=120, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert expected in result.stdout
    if filename == "03_demo_oaep.py":
        assert "Eve lấy lại plaintext bằng cách cũ: False" in result.stdout
    if filename == "04_attack_lab.py":
        assert "Trạng thái: recovered; khớp thông điệp gốc: True" in result.stdout
    if filename == "05_conditions_analyzer.py":
        assert "\n 180 " in result.stdout
        assert "Tối thiểu" in result.stdout
    assert list(tmp_path.iterdir()) == []
