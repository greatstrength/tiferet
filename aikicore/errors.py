class AppError(Exception):

    def __init__(self, error_name: str, lang: str = 'en_US', **format_args):
        super().__init__(self)
        self.error_name = error_name
        self.lang = lang
        self.format_args = format_args


class DomainError(AppError):

    def __init__(self, error_name: str, lang: str = 'en_US', **format_args):
        super().__init__(error_name, lang, **format_args)