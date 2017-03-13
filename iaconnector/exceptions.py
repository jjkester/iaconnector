class OAuthError(Exception):
    """Base error class for OAuth exceptions."""
    def __init__(self, message):
        """
        :param message: The error message.
        """
        self.message = str(message)

    def __str__(self):
        return self.message


class APIError(Exception):
    """Base error class for API exceptions."""
    error_code = None

    def __init__(self, message, error_code=None):
        """
        :param message: The error message.
        :param error_code: The (integer) error code.
        """
        self.message = str(message)

        if error_code is not None:
            assert isinstance(error_code, int)
            self.error_code = error_code

    def __str__(self):
        error = self.error_code if str(self.error_code) is None else "unknown"
        return "{:s}: {:s}".format(error, self.message)


class NotLoggedInError(APIError):
    """The given token is rejected."""
    error_code = 403


class UnknownDeviceError(APIError):
    """The given device id is rejected."""
    error_code = 406


class SignupError(APIError):
    """Could not sign up the user for the event."""
    error_code = 412


class OtherError(APIError):
    """Unexpected error."""
    error_code = 500
