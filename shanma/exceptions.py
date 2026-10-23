"""
ShanMa SMS SDK - Exception Hierarchy
"""


class ShanmaError(Exception):
    """Base exception for all ShanMa SMS SDK errors."""
    pass


class AuthenticationError(ShanmaError):
    """Raised when API authentication fails (invalid API key or unauthorized)."""
    pass


class InsufficientBalanceError(ShanmaError):
    """Raised when account balance is insufficient to place an order."""
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


class ActivationNotFoundError(ShanmaError):
    """Raised when the specified activation ID is not found or has expired."""
    pass
