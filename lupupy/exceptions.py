"""The exceptions used by Lupupy."""


class LupusecException(Exception):
    """Raised when the panel cannot be reached or answers unexpectedly."""

    def __init__(self, message: str, details: str | None = None):
        """Initialize LupusecException."""
        super().__init__(message)

        self.message = message
        self.details = details


class LupusecNotSupportedException(LupusecException):
    """Raised when the connected panel cannot do what was asked.

    The first XT1 knows neither switching nor shutters, area names, device
    details or an event log, and no panel takes a mode or area it does not
    have. The calling application decides what to do about it.
    """
