from .base import RetailerAdapter
from .nike import NikeAdapter
from .sephora import SephoraAdapter


RETAILER_ADAPTERS: dict[str, RetailerAdapter] = {
    "nike": NikeAdapter(),
    "sephora": SephoraAdapter(),
}


def get_price_adapter(retailer: str | None) -> RetailerAdapter | None:
    if not retailer:
        return None
    return RETAILER_ADAPTERS.get(retailer.lower())


def get_delivery_adapter(retailer: str | None) -> RetailerAdapter | None:
    if not retailer:
        return None
    return RETAILER_ADAPTERS.get(retailer.lower())
