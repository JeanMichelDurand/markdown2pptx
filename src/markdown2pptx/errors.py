"""The one error bad input can raise: the command line prints its message, without a traceback."""


class InputError(ValueError):
    """The input cannot be processed; the message says why, in words a user understands."""
