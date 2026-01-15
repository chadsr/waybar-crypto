class WaybarCryptoException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NoApiKeyException(WaybarCryptoException):
    pass


class CoinmarketcapApiException(WaybarCryptoException):
    def __init__(self, message: str, error_code: int | None) -> None:
        super().__init__(message)
        self.error_code = error_code

    def __str__(self) -> str:
        return f"{self.message} ({self.error_code})"
