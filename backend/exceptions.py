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


class InvalidEmailError(Exception):
    """Raised when the email domain is not allowed."""

    pass


class UninvitedUserError(Exception):
    """Raised when the user is not in the allowed users list."""

    pass


class DeactivatedUserError(Exception):
    """Raised when the user account has been deactivated."""

    pass


class IncompleteProfileError(Exception):
    """Raised when the user profile is incomplete."""

    pass


class InvalidTokenError(Exception):
    """Raised when the provided token is invalid."""

    pass


class InvalidUserCredentialsError(Exception):
    """Raised when user credentials are invalid."""

    pass


class UserNotFoundError(Exception):
    """Raised when a user is not found in the database."""

    pass
