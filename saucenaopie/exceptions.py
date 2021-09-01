class SauceNaoError(Exception):  # TODO: Add SauceNao message
    pass


class UnknownError(SauceNaoError):
    def __init__(self, message: str, status_code: int = 200) -> None:
        self.status_code = status_code
        super().__init__(message)


class UnknownServerError(UnknownError):
    pass


class UnknownClientError(UnknownError):
    pass


class LimitReached(SauceNaoError):
    def __init__(
        self, message: str, long_remaining: int, short_remaining: int, long_limit: int, short_limit: int
    ) -> None:
        self.long_remaining = long_remaining
        self.short_remaining = short_remaining
        self.long_limit = long_limit
        self.short_limit = short_limit
        super().__init__(message)


class ShortLimitReached(LimitReached):
    pass


class LongLimitReached(LimitReached):
    pass


class BadAPIKey(SauceNaoError):
    pass


class TooManyFailedRequests(SauceNaoError):
    pass


class ImageInvalid(SauceNaoError):
    pass


class FileIsTooLarge(ImageInvalid):
    pass


class AccountBanned(SauceNaoError):
    pass
