"""
Codex SMS Python SDK.
Official client library for Codex SMS verification services (https://shanma.store).
"""

from shanma import (
    CodexSmsClient,
    ShanmaClient,
    ActivationContext,
    OrderResult,
    SmsResult,
    normalize_service,
    SERVICE_ALIASES,
    CodexSmsError,
    ShanmaError,
    AuthenticationError,
    ConflictError,
    RateLimitError,
    CdkAlreadyUsedError,
    ActivationNotFoundError,
    TimeoutError,
    UpstreamCarrierError,
    NumberUnavailableError,
    InsufficientBalanceError,
    __version__,
    __all__,
)
