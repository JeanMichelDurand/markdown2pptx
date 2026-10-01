"""The one error bad input can raise: the command line prints its message, without a traceback."""


class InputError(ValueError):
    """The Markdown cannot be converted; the message says why, in words a user understands."""


class TemplateError(InputError):
    """The --template file cannot be used; the message says why."""
