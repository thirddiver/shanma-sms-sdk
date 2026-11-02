"""
Codex SMS SDK - Exception Hierarchy
"""


class ShanmaError(Exception):
    """Base exception for all Codex SMS SDK errors."""
    pass


# Brand alias for base exception
CodexSmsError = ShanmaError


class AuthenticationError(CodexSmsError):
    """Raised when API authentication fails (invalid CDK or unauthorized)."""
    pass


class RateLimitError(CodexSmsError):
    """Raised when API rate limit (per-IP or per-CDK) is exceeded (HTTP 429)."""
    pass


class CdkAlreadyUsedError(CodexSmsError):
    """Raised when CDK has already been redeemed or expired (HTTP 410)."""
    pass


class ActivationNotFoundError(CodexSmsError):
    """Raised when the specified CDK or activation ID is not found (HTTP 404)."""
    pass


class TimeoutError(CodexSmsError):
    """Raised when waiting for incoming SMS verification code exceeds timeout."""
    pass


class UpstreamCarrierError(CodexSmsError):
    """Raised when upstream mobile network operator fails or returns an error."""
    pass


class NumberUnavailableError(CodexSmsError):
    """Raised when no numbers are available for the requested service/country."""
    pass


class InsufficientBalanceError(CodexSmsError):
    """Raised when account balance or credits are insufficient."""
    pass
