"""
Codex SMS Python SDK
Official client library for Codex SMS verification and overseas mobile number services (https://shanma.store).
"""

from .client import (
    CodexSmsClient,
    ShanmaClient,
    ActivationContext,
    OrderResult,
    SmsResult,
    normalize_service,
    SERVICE_ALIASES,
)
from .exceptions import (
    CodexSmsError,
    ShanmaError,
    AuthenticationError,
    RateLimitError,
    CdkAlreadyUsedError,
    ActivationNotFoundError,
    TimeoutError,
    UpstreamCarrierError,
    NumberUnavailableError,
    InsufficientBalanceError,
)

__version__ = "0.3.1"
__all__ = [
    "CodexSmsClient",
    "ShanmaClient",
    "ActivationContext",
    "OrderResult",
    "SmsResult",
    "normalize_service",
    "SERVICE_ALIASES",
    "CodexSmsError",
    "ShanmaError",
    "AuthenticationError",
    "RateLimitError",
    "CdkAlreadyUsedError",
    "ActivationNotFoundError",
    "TimeoutError",
    "UpstreamCarrierError",
    "NumberUnavailableError",
    "InsufficientBalanceError",
]
