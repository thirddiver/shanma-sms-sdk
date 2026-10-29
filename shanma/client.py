"""
Codex SMS API Client.
"""

import time
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass

from .exceptions import (
    ShanmaError,
    AuthenticationError,
    InsufficientBalanceError,
    TimeoutError,
    UpstreamCarrierError,
    ActivationNotFoundError,
    NumberUnavailableError,
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


def normalize_service(service: str) -> str:
    """
    Normalize human-readable service aliases or short codes to canonical names.
    Examples:
        normalize_service("chatgpt") -> "openai"
        normalize_service("dr") -> "openai"
        normalize_service("go") -> "google"
        normalize_service("custom_app") -> "custom_app"
    """
    cleaned = (service or "").strip().lower()
    return SERVICE_ALIASES.get(cleaned, cleaned)


@dataclass
class OrderResult:
    """Represents a virtual phone number reservation order."""
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
    Pythonic Context Manager for ordering virtual numbers and polling SMS codes.
    Guarantees automatic cancellation and credit protection if no SMS is received.

    Example:
        >>> with client.activation(service="openai", country="usa") as act:
        >>>     print(f"Assigned phone: {act.order.phone_number}")
        >>>     sms = act.wait_for_sms(timeout=180)
        >>>     if sms:
        >>>         print(f"Received code: {sms.code}")
        # Automatically calls cancel_order if exiting without receiving code
    """

    def __init__(
        self,
        client: "ShanmaClient",
        service: str,
        country: str = "usa",
        auto_cancel: bool = True
    ):
        self.client = client
        self.service = service
        self.country = country
        self.auto_cancel = auto_cancel
        self.order: Optional[OrderResult] = None
        self.sms: Optional[SmsResult] = None

    def __enter__(self) -> "ActivationContext":
        self.order = self.client.order_number(service=self.service, country=self.country)
        return self

    def wait_for_sms(
        self,
        timeout: int = 300,
        interval: int = 5,
        on_poll: Optional[Callable[[int, float], None]] = None
    ) -> Optional[SmsResult]:
        if not self.order:
            raise ShanmaError("No active order found in context.")
        self.sms = self.client.wait_for_sms(
            activation_id=self.order.activation_id,
            timeout=timeout,
            interval=interval,
            on_poll=on_poll
        )
        return self.sms

    def cancel(self) -> bool:
        """Manually trigger order cancellation."""
        if self.order:
            return self.client.cancel_order(self.order.activation_id)
        return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.auto_cancel and self.order and not self.sms:
            try:
                self.cancel()
            except Exception:
                pass
        return False


class ShanmaClient:
    """
    Client for interacting with Codex SMS verification service.
    
    Example:
        >>> client = ShanmaClient(api_key="your_api_key")
        >>> order = client.order_number(service="openai", country="usa")
        >>> sms = client.wait_for_sms(order.activation_id, timeout=300)
    """

    DEFAULT_BASE_URL = "https://api.shanma.store"
    VERSION = "0.2.0"

    def __init__(self, api_key: str, base_url: Optional[str] = None, timeout: int = 30):
        self.api_key = api_key.strip() if api_key else ""
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout

        if not self.api_key:
            raise AuthenticationError("API key is required to initialize ShanmaClient.")

    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, method: str = "GET") -> Dict[str, Any]:
        """Make an authenticated HTTP request to Codex SMS API."""
        query_params = {"token": self.api_key}
        if params:
            query_params.update(params)

        query_string = urllib.parse.urlencode({k: str(v) for k, v in query_params.items() if v is not None})
        url = f"{self.base_url}{endpoint}?{query_string}"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": f"Shanma-SMS-SDK/{self.VERSION} (Python)",
                "Accept": "application/json"
            },
            method=method
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise AuthenticationError(f"Authentication failed: HTTP {e.code}")
            if e.code == 404:
                raise ActivationNotFoundError(f"Resource not found: HTTP 404 on {endpoint}")
            raise ShanmaError(f"HTTP request error: {e}")
        except Exception as e:
            raise ShanmaError(f"Connection error: {e}")

    def get_balance(self) -> float:
        """Check current account balance."""
        res = self._request("/api/user/balance")
        return float(res.get("balance", 0.0))

    def get_available_services(self, country: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query available verification services and current stock."""
        params = {"country": country} if country else None
        res = self._request("/api/services/list", params=params)
        return res.get("services", [])

    def order_number(self, service: str, country: str = "usa") -> OrderResult:
        """
        Request a temporary virtual number for a specific service and country.
        Automatically normalizes service aliases (e.g. 'chatgpt' -> 'openai', 'go' -> 'google').
        """
        canonical_service = normalize_service(service)
        params = {
            "service": canonical_service,
            "country": country
        }
        res = self._request("/api/order/create", params=params, method="POST")

        if not res.get("success"):
            msg = res.get("message", "Failed to order number")
            lower_msg = msg.lower()
            if "balance" in lower_msg:
                raise InsufficientBalanceError(msg)
            if "no numbers" in lower_msg or "out of stock" in lower_msg:
                raise NumberUnavailableError(msg)
            raise UpstreamCarrierError(msg)

        return OrderResult(
            activation_id=str(res.get("activation_id") or res.get("order_id")),
            phone_number=str(res.get("phone_number") or res.get("number")),
            service=canonical_service,
            country=country,
            raw=res
        )

    def query_sms(self, activation_id: str) -> Optional[SmsResult]:
        """Check current SMS status for an order."""
        res = self._request("/api/order/sms", params={"activation_id": activation_id})
        
        status = res.get("status")
        if status in ("received", "done", "success") and res.get("sms_code"):
            return SmsResult(
                code=str(res.get("sms_code")),
                full_text=str(res.get("sms_text", "")),
                raw=res
            )
        return None

    def wait_for_sms(
        self,
        activation_id: str,
        timeout: int = 300,
        interval: int = 5,
        on_poll: Optional[Callable[[int, float], None]] = None
    ) -> Optional[SmsResult]:
        """
        Poll until an SMS code arrives or the timeout limit is reached.
        
        Args:
            activation_id: Order activation identifier.
            timeout: Maximum seconds to wait (default: 300s).
            interval: Polling frequency in seconds (default: 5s).
            on_poll: Optional callback invoked on each poll attempt (attempt, elapsed_seconds).
        """
        start_time = time.time()
        attempt = 0
        while time.time() - start_time < timeout:
            attempt += 1
            elapsed = time.time() - start_time
            if on_poll:
                try:
                    on_poll(attempt, elapsed)
                except Exception:
                    pass

            sms = self.query_sms(activation_id)
            if sms:
                return sms
            time.sleep(interval)
        return None

    def cancel_order(self, activation_id: str) -> bool:
        """
        Cancel an unfulfilled order and trigger credit refund.
        """
        res = self._request("/api/order/cancel", params={"activation_id": activation_id}, method="POST")
        return bool(res.get("success", False))

    def activation(
        self,
        service: str,
        country: str = "usa",
        auto_cancel: bool = True
    ) -> ActivationContext:
        """
        Convenience factory for ActivationContext manager.
        """
        return ActivationContext(
            client=self,
            service=service,
            country=country,
            auto_cancel=auto_cancel
        )
