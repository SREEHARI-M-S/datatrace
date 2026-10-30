import json
from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app

runner = CliRunner()


def test_explain_json_writes_output(tmp_path: Path) -> None:
    out = tmp_path / "explain.json"
    result = runner.invoke(
        app,
        ["explain", "--record", "customer_id=183729", "--json", "-o", str(out)],
    )
    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["record_id"] == "183729"
    assert payload["root_cause"]
