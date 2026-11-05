"""Errors have explicit disposition; infrastructure failure never means bad data."""


class PocError(Exception):
    code = "E_SYSTEM"


class DataError(PocError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


class EnvelopeError(DataError):
    def __init__(self, message):
        super().__init__("E_ENVELOPE", message)


class IdentityCollision(PocError):
    code = "E_IDENTITY_COLLISION"


class CapacityError(PocError):
    code = "E_CAPACITY"


class Retryable(PocError):
    """An unresolved delivery remains owned by the broker/source."""


class SystemFailure(PocError):
    """Pause rather than acknowledge an unclassified/systemic error."""
