"""
Codex SMS (ShanMa) Python SDK
Official client library for Codex SMS verification and virtual phone number services.
"""

from .client import ShanmaClient, OrderResult, SmsResult
from .exceptions import (
    ShanmaError,
    AuthenticationError,
    InsufficientBalanceError,
    TimeoutError,
    UpstreamCarrierError,
)

# Brand alias: CodexSmsClient points to ShanmaClient for unified branding
CodexSmsClient = ShanmaClient

__version__ = "0.1.0"
__all__ = [
    "ShanmaClient",
    "CodexSmsClient",
    "OrderResult",
    "SmsResult",
    "ShanmaError",
    "AuthenticationError",
    "InsufficientBalanceError",
    "TimeoutError",
    "UpstreamCarrierError",
]
