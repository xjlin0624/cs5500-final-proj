class RetailerScrapeError(RuntimeError):
    status = "scrape_failed"

    def __init__(self, message: str, *, retryable: bool = True):
        super().__init__(message)
        self.retryable = retryable


class RetailerUnsupportedError(RetailerScrapeError):
    status = "unsupported_retailer"

    def __init__(self, message: str = "Retailer is not supported for this operation."):
        super().__init__(message, retryable=False)


class RetailerNotReadyError(RetailerScrapeError):
    status = "scraper_not_ready"

    def __init__(self, message: str):
        super().__init__(message, retryable=False)


class RetailerRateLimitedError(RetailerScrapeError):
    status = "scraper_rate_limited"

    def __init__(self, message: str = "Retailer scraping is rate limited."):
        super().__init__(message, retryable=True)


class RetailerCircuitOpenError(RetailerScrapeError):
    status = "scraper_circuit_open"

    def __init__(self, message: str = "Retailer scraping circuit is open."):
        super().__init__(message, retryable=False)


class ScraperTransientError(RetailerScrapeError):
    status = "scraper_transient_failure"

    def __init__(self, message: str):
        super().__init__(message, retryable=True)
