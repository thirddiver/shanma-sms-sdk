"""
Codex SMS Python SDK
Official client library for Codex SMS verification and virtual phone number services.
"""

from .client import (
    ShanmaClient,
    ActivationContext,
    OrderResult,
    SmsResult,
    normalize_service,
    SERVICE_ALIASES,
)
from .exceptions import (
    ShanmaError,
    AuthenticationError,
    InsufficientBalanceError,
    TimeoutError,
    UpstreamCarrierError,
    NumberUnavailableError,
    ActivationNotFoundError,
)

# Brand alias: CodexSmsClient points to ShanmaClient for unified branding
CodexSmsClient = ShanmaClient

__version__ = "0.2.0"
__all__ = [
    "ShanmaClient",
    "CodexSmsClient",
    "ActivationContext",
    "OrderResult",
    "SmsResult",
    "normalize_service",
    "SERVICE_ALIASES",
    "ShanmaError",
    "AuthenticationError",
    "InsufficientBalanceError",
    "TimeoutError",
    "UpstreamCarrierError",
    "NumberUnavailableError",
    "ActivationNotFoundError",
]
