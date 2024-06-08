class AppError(Exception):

    def __init__(self, error_name: str, *format_args):
        super().__init__(self)
        self.error_name = error_name
        self.format_args = format_args


class DomainError(AppError):

    def __init__(self, error_name: str, *format_args):
        super().__init__(error_name, *format_args)


class InvalidRequestData(AppError):

    def __init__(self, *format_args):
        super().__init__('INVALID_REQUEST_DATA', *format_args)