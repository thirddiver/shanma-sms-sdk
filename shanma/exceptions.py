"""
Codex SMS SDK - Exception Hierarchy
"""


class ShanmaError(Exception):
    """Base exception for all Codex SMS SDK errors."""
    pass


# Brand alias for base exception
CodexSmsError = ShanmaError


class AuthenticationError(CodexSmsError):
    """Raised when API authentication fails (invalid CDK or unauthorized, HTTP 401/403)."""
    pass


class ConflictError(CodexSmsError):
    """Raised when operation conflicts with current state or requires confirmation (HTTP 409)."""
    pass


class RateLimitError(CodexSmsError):
    """Raised when API rate limit (per-IP or per-CDK) is exceeded (HTTP 429)."""
    pass


class CdkAlreadyUsedError(CodexSmsError):
    """Raised when CDK has already been redeemed or expired (HTTP 410)."""
    pass


class ActivationNotFoundError(CodexSmsError):
    """Raised when the CDK/resource is not found (HTTP 404) or session status is 'expired'."""
    pass


class TimeoutError(CodexSmsError):
    """Optional SDK timeout exception class for callers; wait_for_sms() returns None on timeout."""
    pass


class UpstreamCarrierError(CodexSmsError):
    """Raised when upstream carrier gateway fails or returns an error (HTTP 502)."""
    pass


class NumberUnavailableError(CodexSmsError):
    """Raised when no numbers are currently available in the pool (HTTP 503)."""
    pass


class InsufficientBalanceError(CodexSmsError):
    """Raised when upstream capacity/balance is unavailable (HTTP 503)."""
    pass
