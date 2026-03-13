from .base import PriceCheckResult, RetailerPriceAdapter


class NikePriceAdapter(RetailerPriceAdapter):
    retailer = "nike"

    def fetch_current_price(self, order_item) -> PriceCheckResult:
        raise NotImplementedError("Nike price adapter is not implemented yet.")


class SephoraPriceAdapter(RetailerPriceAdapter):
    retailer = "sephora"

    def fetch_current_price(self, order_item) -> PriceCheckResult:
        raise NotImplementedError("Sephora price adapter is not implemented yet.")


PRICE_ADAPTERS: dict[str, RetailerPriceAdapter] = {
    "nike": NikePriceAdapter(),
    "sephora": SephoraPriceAdapter(),
}


def get_price_adapter(retailer: str | None) -> RetailerPriceAdapter | None:
    if not retailer:
        return None
    return PRICE_ADAPTERS.get(retailer.lower())
