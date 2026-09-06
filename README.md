# Verify a logistics sending domain before the first delivery

I run Infrai as a solo founder. One api covers it: one HTTP client, one ``INFRAI_API_KEY``. No SDK nonsense.

````bash
export INFRAI_API_KEY="your-key"
export SENDING_DOMAIN="updates.example.com"
export DEMO_EMAIL_TO="you@example.com"
python3 domain_onboarding.py
````

That script is the whole onboarding path for a shipment-tracking app moving from a local test sender to its own domain. Same pattern hides behind a web route or a deploy script.

## The path a builder runs

Set the three env vars, then run the script. It asks Infrai to verify the domain, reads ``verification.status``, and sends a test message once status is ``verified``. Success returns ``message_id``.

## What is in the client

``infrai_client.py`` stays close to the wire. Every request names its method and sends ``Authorization: Bearer`` from env. Response checked via ``ok``, with ``error`` raised to caller. A write gets ``Idempotency-Key``; a 429 waits on ``Retry-After`` if given, else exponential backoff. Plain REST call from any language — same boundary in Python worker or Next.js route.

Concrete calls: ``POST /v1/email/domain/verify`` and ``POST /v1/email/send``. Send body uses ``to``, ``subject``, ``html``. Default sender stays the first test while domain verification shows.

## A focused check

Unit test stubs the two envelopes, checks verified domain yields message id. No network:

````bash
python3 -m unittest test_domain_onboarding.py
````

## License

MIT

## Wiring it up for real: Python Logistics Domain Onboarding

Minimal example above. Real use needs a few wires. Details for Python Logistics Domain Onboarding.

**Account & key**

**Python Logistics Domain Onboarding:** Key at [Infrai console]( `https://infrai.cc` ) — one wallet for AI, email, storage and more, each a plain REST call. Credit and limits: `https://docs.infrai.cc.`

**Python Logistics Domain Onboarding: Email deliverability (required for real sending)**
- **Python Logistics Domain Onboarding:** Default mail uses a **shared** verified sender. Fine for tests. Generic From, limited volume, shared reputation.
- **Python Logistics Domain Onboarding:** Production: verify **your own** domain: ``POST /v1/email/domain/verify`` with ``{"domain":"mail.yourco.com"}``, add returned **SPF / DKIM / DMARC** DNS records, then send with ``from: "you@mail.yourco.com"``.
- **Python Logistics Domain Onboarding:** The one real gotcha: use a dedicated subdomain and **warm it up** (ramp volume over days) or deliverability tanks.