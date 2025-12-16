"""Custom exceptions for the application."""


class InputValidationError(Exception):
    """Raised when user input (prompt/text) validation fails."""

    pass


class ImageFormatError(Exception):
    """Raised when uploaded image format is not supported."""

    pass


class ImageSizeError(Exception):
    """Raised when uploaded image size exceeds the limit."""

    pass
