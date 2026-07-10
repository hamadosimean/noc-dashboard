from app.services import notification_service as ns


def test_sms_skipped_when_unconfigured():
    assert ns.send_sms("test") == 0


def test_email_skipped_when_unconfigured():
    assert ns.send_email("subject", "body") == 0


def test_notify_disabled_sends_nothing(monkeypatch):
    called = []
    monkeypatch.setattr(ns, "NOTIFICATIONS_ENABLED", False)
    monkeypatch.setattr(ns, "send_sms", lambda body: called.append(("sms", body)))
    monkeypatch.setattr(ns, "send_email", lambda subject, body: called.append(("email", body)))
    ns.notify_critical_incident(1, "DED-001", "DREP Dédougou", "critical", "2026-05-17", "panne", None)
    assert called == []


def test_notify_sends_sms_and_email(monkeypatch):
    called = []
    monkeypatch.setattr(ns, "NOTIFICATIONS_ENABLED", True)
    monkeypatch.setattr(ns, "send_sms", lambda body: called.append(("sms", body)) or 1)
    monkeypatch.setattr(
        ns, "send_email", lambda subject, body: called.append(("email", subject + body)) or 1
    )
    ns.notify_critical_incident(
        4821, "DED-001", "DREP Dédougou", "critical", "2026-05-17T03:22:00",
        "Perte de connectivité", "TKT-2026-04821",
    )
    kinds = [k for k, _ in called]
    assert kinds == ["sms", "email"]
    sms_body = called[0][1]
    assert "DED-001" in sms_body and "CRITICAL" in sms_body and "TKT-2026-04821" in sms_body
    email_content = called[1][1]
    assert "DED-001" in email_content and "#4821" in email_content


def test_notify_never_raises(monkeypatch):
    def boom(body):
        raise RuntimeError("provider down")

    monkeypatch.setattr(ns, "NOTIFICATIONS_ENABLED", True)
    monkeypatch.setattr(ns, "send_sms", boom)
    # Must swallow the exception — ingestion depends on it.
    ns.notify_critical_incident(1, "OUA-003", "Nœud Ouaga", "critical", "2026-06-01", None, None)


def test_sms_posts_to_twilio(monkeypatch):
    posts = []

    class FakeResponse:
        def raise_for_status(self):
            pass

    def fake_post(url, auth=None, data=None, timeout=None):
        posts.append((url, auth, data))
        return FakeResponse()

    monkeypatch.setattr(ns, "TWILIO_ACCOUNT_SID", "AC123")
    monkeypatch.setattr(ns, "TWILIO_AUTH_TOKEN", "tok")
    monkeypatch.setattr(ns, "TWILIO_FROM_NUMBER", "+15550000000")
    monkeypatch.setattr(ns, "NOC_SMS_RECIPIENTS", ["+22670000001", "+22670000002"])
    monkeypatch.setattr(ns.requests, "post", fake_post)

    assert ns.send_sms("alerte") == 2
    assert all("AC123" in url for url, _, _ in posts)
    assert posts[0][2]["To"] == "+22670000001"
    assert posts[1][2]["To"] == "+22670000002"
