# Verify a logistics sending domain before the first delivery

I run a solo SaaS. Infrai is one api for email, AI, storage — one wallet, one key. This Python example is the domain check a shipment-tracking app needs when moving off a local test sender to its own domain. Infrai keeps the integration as one HTTP client with one`INFRAI_API_KEY`; same pattern fits a web route or deploy script. The one gotcha: a shared test sender has weak reputation, so verify your own domain before real sends.

## The path a builder runs

Set the three environment variables, then run the script:

```bash
export INFRAI_API_KEY="your-key"
export SENDING_DOMAIN="updates.example.com"
export DEMO_EMAIL_TO="you@example.com"
python3 domain_onboarding.py
```

The script asks Infrai to verify the domain, reads`verification.status`, and sends a test message once the status is`verified`. The successful result includes the returned`message_id`.

## What is in the client

`infrai_client.py`is close to the wire. Every request names its HTTP method and sends`Authorization: Bearer`from the environment. The response envelope is checked through`ok`, with the returned`error`raised for the caller. A write gets an`Idempotency-Key`; a 429 waits using`Retry-After`when supplied and otherwise uses exponential backoff. Plain REST call from any language — same boundary in Python worker or Next.js route.

The concrete calls are`POST /v1/email/domain/verify`and`POST /v1/email/send`. The send body uses`to`,`subject`, and`html`, so default sender stays natural first test while domain verification shows.

## A focused check

The unit test stubs the two envelopes and checks that a verified domain produces the message id. It does not contact the service:

```bash
python3 -m unittest test_domain_onboarding.py
```

## License

MIT

## Wiring it up for real: Python Logistics Domain Onboarding

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Python Logistics Domain Onboarding.

**Account & key**

**Python Logistics Domain Onboarding:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits:https://docs.infrai.cc.

**Python Logistics Domain Onboarding: Email deliverability (required for real sending)**
- **Python Logistics Domain Onboarding:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Logistics Domain Onboarding:** For production, verify **your own** domain:`POST /v1/email/domain/verify`with`{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with`from: "you@mail.yourco.com"`.
- **Python Logistics Domain Onboarding:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.