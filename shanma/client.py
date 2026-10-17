"""
ShanMa SMS API Client.
"""

import time
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from .exceptions import (
    ShanmaError,
    AuthenticationError,
    InsufficientBalanceError,
    TimeoutError,
    UpstreamCarrierError
)

@dataclass
class OrderResult:
    activation_id: str
    phone_number: str
    service: str
    country: str
    raw: Dict[str, Any]

@dataclass
class SmsResult:
    code: str
    full_text: str
    raw: Dict[str, Any]

class ShanmaClient:
    """
    Client for interacting with ShanMa SMS verification service.
    
    Example:
        >>> client = ShanmaClient(api_key="your_api_key")
        >>> order = client.order_number(service="openai", country="usa")
        >>> sms = client.wait_for_sms(order.activation_id, timeout=300)
    """

    DEFAULT_BASE_URL = "https://api.shanma.store"

    def __init__(self, api_key: str, base_url: Optional[str] = None, timeout: int = 30):
        self.api_key = api_key.strip() if api_key else ""
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout

        if not self.api_key:
            raise AuthenticationError("API key is required to initialize ShanmaClient.")

    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, method: str = "GET") -> Dict[str, Any]:
        """Make an authenticated HTTP request to ShanMa API."""
        query_params = {"token": self.api_key}
        if params:
            query_params.update(params)

        query_string = urllib.parse.urlencode({k: str(v) for k, v in query_params.items() if v is not None})
        url = f"{self.base_url}{endpoint}?{query_string}"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Shanma-SMS-SDK/0.1.0 (Python)",
                "Accept": "application/json"
            },
            method=method
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data
        except urllib.error.HTTPError as e:
            if e.code == 401 or e.code == 403:
                raise AuthenticationError(f"Authentication failed: HTTP {e.code}")
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
        """
        params = {
            "service": service,
            "country": country
        }
        res = self._request("/api/order/create", params=params, method="POST")

        if not res.get("success"):
            msg = res.get("message", "Failed to order number")
            if "balance" in msg.lower():
                raise InsufficientBalanceError(msg)
            raise UpstreamCarrierError(msg)

        return OrderResult(
            activation_id=str(res.get("activation_id") or res.get("order_id")),
            phone_number=str(res.get("phone_number") or res.get("number")),
            service=service,
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

    def wait_for_sms(self, activation_id: str, timeout: int = 300, interval: int = 5) -> Optional[SmsResult]:
        """
        Poll until an SMS code arrives or the timeout limit is reached.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
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
