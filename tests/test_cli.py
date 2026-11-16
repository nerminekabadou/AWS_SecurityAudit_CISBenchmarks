import json

from click.testing import CliRunner

from Cli import main as cli
from Core import orchestrator


def test_invalid_credentials_exit_with_error(monkeypatch):
    monkeypatch.setattr(orchestrator, "validate_creds",
                        lambda *a, **k: (False, "Invalid AWS Access Key ID", None))
    result = CliRunner().invoke(cli.main, ["--profile", "nope"])
    assert result.exit_code != 0
    assert "Invalid AWS Access Key ID" in result.output


def test_json_output_is_valid_json(monkeypatch):
    monkeypatch.setattr(orchestrator, "validate_creds", lambda *a, **k: (True, "ok", object()))
    monkeypatch.setattr(orchestrator, "discover_enabled_services", lambda s: ["iam"])
    monkeypatch.setattr(orchestrator, "thread_audits", lambda services, s: [[
        {"service": "iam", "check_id": "CIS-1.1", "status": "PASS"},
    ]])
    result = CliRunner().invoke(cli.main, ["--output", "json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {"iam": [{"service": "iam", "check_id": "CIS-1.1", "status": "PASS"}]}
