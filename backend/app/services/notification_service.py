"""
Notifications on critical incidents (cahier des charges §7 step 6):
SMS to the NOC lead via Twilio + permanence email via SMTP.

Both channels degrade gracefully: if credentials are missing or the provider is
unreachable, the failure is logged and ingestion continues — an alerting outage
must never block the incident pipeline.
"""
import logging
import smtplib
from email.mime.text import MIMEText

import requests

from app.core.constants import (
    NOC_EMAIL_RECIPIENTS,
    NOC_SMS_RECIPIENTS,
    NOTIFICATIONS_ENABLED,
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USER,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM_NUMBER,
)

logger = logging.getLogger(__name__)

TWILIO_MESSAGES_URL = (
    "https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
)


def _sms_configured() -> bool:
    return bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER and NOC_SMS_RECIPIENTS)


def _email_configured() -> bool:
    return bool(SMTP_HOST and NOC_EMAIL_RECIPIENTS)


def send_sms(body: str) -> int:
    """Send `body` to every configured NOC number. Returns the count sent."""
    if not _sms_configured():
        logger.info("SMS not configured, skipping notification")
        return 0
    sent = 0
    url = TWILIO_MESSAGES_URL.format(sid=TWILIO_ACCOUNT_SID)
    for number in NOC_SMS_RECIPIENTS:
        try:
            resp = requests.post(
                url,
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                data={"From": TWILIO_FROM_NUMBER, "To": number, "Body": body},
                timeout=10,
            )
            resp.raise_for_status()
            sent += 1
        except requests.RequestException as exc:
            logger.error("SMS to %s failed: %s", number, exc)
    return sent


def send_email(subject: str, body: str) -> int:
    """Send a plain-text email to the NOC permanence list. Returns the count sent."""
    if not _email_configured():
        logger.info("SMTP not configured, skipping notification")
        return 0
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = ", ".join(NOC_EMAIL_RECIPIENTS)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            if SMTP_USE_TLS:
                smtp.starttls()
            if SMTP_USER:
                smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.sendmail(SMTP_FROM, NOC_EMAIL_RECIPIENTS, msg.as_string())
        return len(NOC_EMAIL_RECIPIENTS)
    except (smtplib.SMTPException, OSError) as exc:
        logger.error("Email notification failed: %s", exc)
        return 0


def notify_critical_incident(
    incident_id: int,
    node_code: str,
    node_name: str,
    severity: str,
    detected_at: str,
    description: str | None,
    itop_ticket_id: str | None,
) -> None:
    """Fire SMS + email for a critical incident. Never raises."""
    if not NOTIFICATIONS_ENABLED:
        return
    try:
        summary = (
            f"[NOC ALERTE {severity.upper()}] {node_code} {node_name} — "
            f"{description or 'incident détecté'} ({detected_at})"
        )
        if itop_ticket_id:
            summary += f" | Ticket {itop_ticket_id}"

        sms_sent = send_sms(summary)
        email_sent = send_email(
            subject=f"[NOC] Incident critique #{incident_id} — {node_code}",
            body=(
                f"Incident critique détecté par la supervision.\n\n"
                f"Nœud       : {node_code} — {node_name}\n"
                f"Sévérité   : {severity}\n"
                f"Détecté à  : {detected_at}\n"
                f"Ticket iTop: {itop_ticket_id or 'N/A'}\n\n"
                f"Description:\n{description or '—'}\n\n"
                f"— NOC Dashboard ANPTIC (message automatique)"
            ),
        )
        logger.info(
            "Critical incident #%s notified (sms=%d, email=%d)",
            incident_id,
            sms_sent,
            email_sent,
        )
    except Exception as exc:  # notification failure must never break ingestion
        logger.exception("Notification for incident #%s failed: %s", incident_id, exc)
