"""
Codex SMS API Client.
Official Python SDK for Codex SMS verification service (https://shanma.store).
"""

from __future__ import annotations

import time
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass

from .exceptions import (
    ShanmaError,
    CodexSmsError,
    AuthenticationError,
    ConflictError,
    RateLimitError,
    CdkAlreadyUsedError,
    ActivationNotFoundError,
    TimeoutError,
    UpstreamCarrierError,
    NumberUnavailableError,
    InsufficientBalanceError,
)

# Common service alias mappings for Developer Experience (DX)
SERVICE_ALIASES: Dict[str, str] = {
    "chatgpt": "openai",
    "openai": "openai",
    "dr": "openai",
    "google": "google",
    "gmail": "google",
    "go": "google",
    "tg": "telegram",
    "telegram": "telegram",
    "wa": "whatsapp",
    "whatsapp": "whatsapp",
    "mm": "microsoft",
    "microsoft": "microsoft",
    "fb": "facebook",
    "facebook": "facebook",
    "ds": "discord",
    "discord": "discord",
    "oi": "tinder",
    "tinder": "tinder",
    "ig": "instagram",
    "instagram": "instagram",
    "tw": "twitter",
    "x": "twitter",
    "twitter": "twitter",
}


def normalize_service(service: Optional[str]) -> Optional[str]:
    """
    Normalize human-readable service aliases or short codes to canonical names.
    Examples:
        normalize_service("chatgpt") -> "openai"
        normalize_service("dr") -> "openai"
        normalize_service("go") -> "google"
        normalize_service("tg") -> "telegram"
    """
    if not service:
        return None
    cleaned = service.strip().lower()
    return SERVICE_ALIASES.get(cleaned, cleaned)


@dataclass
class OrderResult:
    """Represents an allocated overseas mobile number reservation."""
    activation_id: str
    phone_number: str
    service: str
    country: str
    raw: Dict[str, Any]


@dataclass
class SmsResult:
    """Represents a received SMS verification payload."""
    code: str
    full_text: str
    raw: Dict[str, Any]


class ActivationContext:
    """
    Pythonic Context Manager for ordering overseas numbers and polling SMS codes.

    Example:
        >>> with client.activation(service="chatgpt") as act:
        >>>     print(f"Allocated phone: {act.phone_number}")
        >>>     sms = act.wait_for_sms(timeout=120)
        >>>     if sms:
        >>>         print(f"Received code: {sms.code}")
        >>>     else:
        >>>         print("Did not receive code, switching phone...")
        >>>         act.switch()
    """

    def __init__(
        self,
        client: "CodexSmsClient",
        service: Optional[str] = None,
    ):
        self.client = client
        self.service = service
        self.order: Optional[OrderResult] = None
        self.sms: Optional[SmsResult] = None

    def __enter__(self) -> "ActivationContext":
        self.order = self.client.redeem(service=self.service)
        return self

    @property
    def phone_number(self) -> str:
        """Returns the currently allocated phone number string."""
        return self.order.phone_number if self.order else ""

    @property
    def activation_id(self) -> str:
        """Returns the currently active activation identifier."""
        return self.order.activation_id if self.order else ""

    def switch(self, confirm_abandon_sms: bool = False) -> OrderResult:
        """
        Request a replacement phone number within per-CDK safety limits.
        If an SMS code was already received on the active number, pass
        confirm_abandon_sms=True (limited to once per single-use CDK).
        """
        self.order = self.client.switch_phone(confirm_abandon_sms=confirm_abandon_sms)
        self.sms = None
        return self.order

    def resend(self) -> Dict[str, Any]:
        """
        Request the upstream carrier to resend the SMS verification code.
        """
        return self.client.resend_sms()

    def wait_for_sms(
        self,
        timeout: int = 180,
        interval: int = 5,
        on_poll: Optional[Callable[[int, float], None]] = None,
    ) -> Optional[SmsResult]:
        """
        Poll for the incoming SMS verification code until received or timed out.
        """
        self.sms = self.client.wait_for_sms(
            timeout=timeout,
            interval=interval,
            on_poll=on_poll,
        )
        return self.sms

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class CodexSmsClient:
    """
    Official Python SDK client for Codex SMS verification service (https://shanma.store).

    Authenticates seamlessly via single-use or multi-use CDK (Card Secret Key)
    acting as a bearer token (`Authorization: Bearer <CDK>`).

    Example:
        >>> from shanma import CodexSmsClient
        >>> client = CodexSmsClient(cdkey="CDK-XXXX-YYYY")
        >>> order = client.redeem(service="chatgpt")
        >>> print(f"Phone number: {order.phone_number}")
        >>> sms = client.wait_for_sms(timeout=120)
        >>> if sms:
        >>>     print(f"Code: {sms.code}")
    """

    DEFAULT_BASE_URL = "https://shanma.store"
    VERSION = "0.3.3"

    def __init__(
        self,
        cdkey: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        raw_token = cdkey or api_key or ""
        self.cdkey = raw_token.strip()
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout

        if not self.cdkey:
            raise AuthenticationError(
                "A valid CDK (or api_key) is required to initialize CodexSmsClient. "
                "Purchase a CDK at https://shanma.store"
            )

    @property
    def api_key(self) -> str:
        """Backwards compatibility alias for cdkey."""
        return self.cdkey

    def _request(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        method: str = "POST",
    ) -> Dict[str, Any]:
        """
        Make an authenticated HTTP request to the Codex SMS API.
        Uses Bearer CDK authentication against /api/guest/cdkeys/*.
        """
        url = f"{self.base_url}{endpoint}"
        payload_bytes = json.dumps(data if data is not None else {}).encode("utf-8")

        headers = {
            "Authorization": f"Bearer {self.cdkey}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"Codex-SMS-SDK/{self.VERSION} (Python)",
        }

        req = urllib.request.Request(
            url,
            data=payload_bytes if method in ("POST", "PUT", "PATCH") else None,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw_body = resp.read().decode("utf-8")
                return json.loads(raw_body) if raw_body else {}
        except urllib.error.HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
                err_json = json.loads(error_body)
                detail = err_json.get("detail", error_body)
            except Exception:
                detail = error_body or str(e)

            if e.code in (401, 403):
                raise AuthenticationError(f"CDK authentication failed (HTTP {e.code}): {detail}")
            if e.code == 404:
                raise ActivationNotFoundError(f"CDK or resource not found (HTTP 404): {detail}")
            if e.code == 409:
                raise ConflictError(f"Operation conflict or confirmation required (HTTP 409): {detail}")
            if e.code == 410:
                raise CdkAlreadyUsedError(f"CDK has already been used or expired (HTTP 410): {detail}")
            if e.code == 429:
                raise RateLimitError(f"API rate limit exceeded (HTTP 429): {detail}")
            if e.code == 502:
                raise UpstreamCarrierError(f"Upstream carrier gateway error (HTTP 502): {detail}")
            if e.code == 503:
                detail_str = str(detail)
                if "余额" in detail_str or "balance" in detail_str.lower():
                    raise InsufficientBalanceError(f"Upstream capacity/balance unavailable (HTTP 503): {detail}")
                raise NumberUnavailableError(f"No numbers currently available (HTTP 503): {detail}")
            raise CodexSmsError(f"HTTP {e.code} error on {endpoint}: {detail}")
        except json.JSONDecodeError as e:
            raise CodexSmsError(f"Invalid JSON response from {url}: {e}")
        except urllib.error.URLError as e:
            raise CodexSmsError(f"Connection error to {url}: {e}")
        except OSError as e:
            raise CodexSmsError(f"Transport/timeout error communicating with {url}: {e}")

    def redeem(self, service: Optional[str] = None) -> OrderResult:
        """
        Redeem the CDK and allocate an overseas mobile number.

        Note:
            In Codex SMS, the target service and routing pool are bound to the
            purchased CDK itself. `/api/guest/cdkeys/redeem` validates `{}` with
            `extra="forbid"`, so `service` is NOT sent on the wire and acts solely
            as an optional local fallback label on `OrderResult.service`.
        """
        canonical_service = normalize_service(service)

        # Wire protocol: GuestCdkeyActionRequest strictly expects empty JSON object {}
        res = self._request("/api/guest/cdkeys/redeem", data={}, method="POST")

        phone = str(res.get("phone") or res.get("phone_number") or "")
        activation_id = str(res.get("activation_id") or "")
        country = str(res.get("country_name") or res.get("country") or "")
        resolved_service = str(res.get("service") or canonical_service or "")

        return OrderResult(
            activation_id=activation_id,
            phone_number=phone,
            service=resolved_service,
            country=country,
            raw=res,
        )

    def order_number(
        self,
        service: Optional[str] = None,
    ) -> OrderResult:
        """
        Deprecated alias for `redeem(service=...)`. Target service and country
        allocation are governed by the purchased CDK and current pool availability.
        """
        return self.redeem(service=service)

    def get_status(self) -> Dict[str, Any]:
        """
        Query current status, remaining time, and allocated number without consuming actions.
        """
        return self._request("/api/guest/cdkeys/status", data={}, method="POST")

    def query_sms(self) -> Optional[SmsResult]:
        """
        Query incoming SMS status for the currently bound phone number.
        Returns SmsResult if received, or None if still waiting.
        Raises ActivationNotFoundError if backend reports status="expired".
        """
        res = self._request("/api/guest/cdkeys/sms", data={}, method="POST")
        status = res.get("status")

        if status == "expired":
            raise ActivationNotFoundError(
                "CDK session is expired, unredeemed, or no longer bound (status='expired')."
            )
        if status == "received" and res.get("code"):
            return SmsResult(
                code=str(res.get("code")),
                full_text=str(res.get("text") or ""),
                raw=res,
            )
        return None

    def wait_for_sms(
        self,
        activation_id: Optional[str] = None,
        timeout: int = 180,
        interval: int = 5,
        on_poll: Optional[Callable[[int, float], None]] = None,
    ) -> Optional[SmsResult]:
        """
        Poll until an SMS verification code arrives or the timeout limit elapses.

        Returns SmsResult when received, or None when timeout elapses without raising TimeoutError.
        Propagates ActivationNotFoundError immediately if status="expired".

        Args:
            activation_id: Optional ID for interface compatibility.
            timeout: Maximum seconds to wait (default: 180s).
            interval: Polling frequency in seconds (default: 5s, clamped to min 4s to prevent 429).
            on_poll: Optional callback invoked on each poll attempt: callback(attempt, elapsed_seconds).
        """
        # Enforce rate limit protection: max 15 requests/min per CDK
        interval = max(interval, 4)
        start_mono = time.monotonic()
        attempt = 0

        while True:
            elapsed = time.monotonic() - start_mono
            if elapsed >= timeout:
                break
            attempt += 1
            if on_poll:
                try:
                    on_poll(attempt, elapsed)
                except Exception:
                    pass

            sms = self.query_sms()
            if sms:
                return sms

            remaining = timeout - (time.monotonic() - start_mono)
            if remaining <= 0:
                break
            time.sleep(min(interval, remaining))

        return None

    def switch_phone(self, confirm_abandon_sms: bool = False) -> OrderResult:
        """
        Request a replacement phone number within per-CDK safety limits (up to 30
        total acquired numbers per CDK; contact support if the limit is reached).

        If an SMS code was already received on the current number, the server
        returns HTTP 409 Conflict unless confirm_abandon_sms=True is supplied
        (abandon-with-code replacement is permitted at most once per single-use CDK).
        """
        payload: Dict[str, Any] = {"confirm_abandon_sms": True} if confirm_abandon_sms else {}
        res = self._request("/api/guest/cdkeys/switch", data=payload, method="POST")
        phone = str(res.get("phone") or res.get("phone_number") or "")
        activation_id = str(res.get("activation_id") or "")
        country = str(res.get("country_name") or res.get("country") or "")
        resolved_service = str(res.get("service") or "")

        return OrderResult(
            activation_id=activation_id,
            phone_number=phone,
            service=resolved_service,
            country=country,
            raw=res,
        )

    def resend_sms(self) -> Dict[str, Any]:
        """
        Request upstream carrier to retry or allow receiving a resend SMS.
        """
        return self._request("/api/guest/cdkeys/resend", data={}, method="POST")

    def activation(
        self,
        service: Optional[str] = None,
    ) -> ActivationContext:
        """
        Convenience factory for the ActivationContext manager.
        """
        return ActivationContext(
            client=self,
            service=service,
        )


# Brand alias
ShanmaClient = CodexSmsClient
