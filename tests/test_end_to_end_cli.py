import json
import subprocess
import sys
from pathlib import Path


def test_cli_schema(tmp_path: Path):
    out = tmp_path / "schema.json"
    cmd = [sys.executable, "-m", "flowfoundry.cli", "schema", str(out)]
    subprocess.run(cmd, check=True)
    assert out.exists()
    data = json.loads(out.read_text())
    assert "properties" in data
