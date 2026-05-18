"""Bridge-specific exception types."""


class BridgeError(Exception):
    """Base exception for expected bridge failures."""


class ConfigurationError(BridgeError):
    """Raised when configuration is missing or invalid."""


class VerificationError(BridgeError):
    """Raised when a webhook cannot be verified."""


class DeliveryError(BridgeError):
    """Raised when outbound delivery fails."""
