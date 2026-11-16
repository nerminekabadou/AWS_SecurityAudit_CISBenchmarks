from Core import auth


class FakeSession:
    created = []

    def __init__(self, **kwargs):
        FakeSession.created.append(kwargs)

    def client(self, name):
        class Sts:
            def get_caller_identity(self):
                return {"Account": "123456789012"}
        return Sts()


def test_uses_profile_when_no_keys(monkeypatch):
    FakeSession.created.clear()
    monkeypatch.setattr(auth.boto3.session, "Session", FakeSession)
    ok, message, _ = auth.validate_creds(region="eu-west-1", profile="audit")
    assert ok and "123456789012" in message
    assert FakeSession.created == [{"profile_name": "audit", "region_name": "eu-west-1"}]


def test_uses_explicit_keys(monkeypatch):
    FakeSession.created.clear()
    monkeypatch.setattr(auth.boto3.session, "Session", FakeSession)
    ok, _, _ = auth.validate_creds("AKIA", "secret", "", "us-east-1")
    assert ok
    assert FakeSession.created[0]["aws_access_key_id"] == "AKIA"
    assert FakeSession.created[0]["aws_session_token"] is None
