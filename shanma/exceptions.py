"""
Codex SMS SDK - Exception Hierarchy
"""


class ShanmaError(Exception):
    """Base exception for all Codex SMS SDK errors."""
    pass


class AuthenticationError(ShanmaError):
    """Raised when API authentication fails (invalid CDK or unauthorized)."""
    pass


class RateLimitError(ShanmaError):
    """Raised when API rate limit (per-IP or per-CDK) is exceeded (HTTP 429)."""
    pass


class CdkAlreadyUsedError(ShanmaError):
    """Raised when CDK has already been redeemed or expired (HTTP 410)."""
    pass


class ActivationNotFoundError(ShanmaError):
    """Raised when the specified CDK or activation ID is not found (HTTP 404)."""
    pass


class TimeoutError(ShanmaError):
    """Raised when waiting for incoming SMS verification code exceeds timeout."""
    pass


class UpstreamCarrierError(ShanmaError):
    """Raised when upstream mobile network operator fails or returns an error."""
    pass


class NumberUnavailableError(ShanmaError):
    """Raised when no numbers are available for the requested service/country."""
    pass


class InsufficientBalanceError(ShanmaError):
    """Raised when account balance or credits are insufficient."""
    pass
