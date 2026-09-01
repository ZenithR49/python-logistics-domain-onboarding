"""Onboard and verify the sending domain for a logistics product."""

import os

from infrai_client import InfraiError, InfraiClient


def onboard_sending_domain(domain: str, test_recipient: str) -> dict[str, object]:
    client = InfraiClient()
    verification = client.request("POST", "/v1/email/domain/verify", {"domain": domain}, write=True)
    status = verification["data"]["verification"]["status"]
    if status != "verified":
        return {"domain": domain, "verification_status": status}

    sent = client.request(
        "POST",
        "/v1/email/send",
        {
            "to": test_recipient,
            "subject": "Logistics sending domain verified",
            "html": f"<p>{domain} is ready for shipment updates.</p>",
        },
        write=True,
    )
    return {"domain": domain, "verification_status": status, "message_id": sent["data"]["message_id"]}


if __name__ == "__main__":
    domain = os.environ.get("SENDING_DOMAIN")
    recipient = os.environ.get("DEMO_EMAIL_TO")
    if not domain or not recipient:
        raise SystemExit("SENDING_DOMAIN and DEMO_EMAIL_TO are required")
    try:
        print(onboard_sending_domain(domain, recipient))
    except InfraiError as error:
        raise SystemExit(str(error)) from error
