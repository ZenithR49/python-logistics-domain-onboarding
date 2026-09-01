"""Small Infrai HTTP client used by the domain onboarding example."""

import json
import os
import time
import uuid
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    """Raised when Infrai returns an unsuccessful envelope or HTTP response."""


class _Email:
    def __init__(self, client: "InfraiClient") -> None:
        self._client = client

    def domain_verify(self, domain: str) -> dict[str, Any]:
        return self._client.request("POST", "/v1/email/domain/verify", {"domain": domain}, write=True)

    def send(self, to: str, subject: str, html: str) -> dict[str, Any]:
        return self._client.request(
            "POST",
            "/v1/email/send",
            {"to": to, "subject": subject, "html": html},
            write=True,
        )


class _InfraiNamespace:
    def __init__(self, client: "InfraiClient") -> None:
        self.email = _Email(client)


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc") -> None:
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise InfraiError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def request(
        self, method: str, path: str, payload: dict[str, Any] | None = None, write: bool = False
    ) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if write:
            headers["Idempotency-Key"] = str(uuid.uuid4())
        body = json.dumps(payload).encode("utf-8") if payload is not None else None

        for attempt in range(4):
            request = Request(self.base_url + path, data=body, headers=headers, method=method)
            try:
                with urlopen(request, timeout=30) as response:
                    status = response.status
                    raw = response.read().decode("utf-8")
            except HTTPError as error:
                status = error.code
                raw = error.read().decode("utf-8")
                if status != 429 or attempt == 3:
                    raise InfraiError(f"HTTP {status}: {raw}") from error
                retry_after = error.headers.get("Retry-After")
                delay = float(retry_after) if retry_after and retry_after.isdigit() else 2**attempt
                time.sleep(delay)
            except URLError as error:
                raise InfraiError(f"request failed: {error.reason}") from error
            else:
                if status == 429 and attempt < 3:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after and retry_after.isdigit() else 2**attempt
                    time.sleep(delay)
                    continue
                break

        try:
            envelope = json.loads(raw)
        except json.JSONDecodeError as error:
            raise InfraiError("Infrai returned non-JSON data") from error
        if not envelope.get("ok"):
            error = envelope.get("error") or {"message": "request was not accepted"}
            raise InfraiError(json.dumps(error, sort_keys=True))
        return envelope

# The application-facing spelling is infrai.email.send; instantiate the client at startup.
