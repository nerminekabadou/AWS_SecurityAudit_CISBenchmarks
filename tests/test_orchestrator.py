from Core import orchestrator


def test_organize_results_groups_by_service():
    report = orchestrator.organize_results([
        [{"service": "iam", "check_id": "1.1"}, {"service": "iam", "check_id": "1.2"}],
        None,
        [{"service": "s3", "check_id": "2.1.1"}],
    ])
    assert {k: len(v) for k, v in report.items()} == {"iam": 2, "s3": 1}


def test_failing_audit_is_reported_not_raised(monkeypatch):
    def boom(name):
        raise RuntimeError("module crashed")
    monkeypatch.setattr(orchestrator.importlib, "import_module", boom)
    [finding] = orchestrator.run_audit("iam", session=None)
    assert finding["status"] == "ERROR" and finding["service"] == "iam"
