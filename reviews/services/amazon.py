from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

@dataclass
class AmazonProductData:
    image_url: Optional[str] = None
    title: Optional[str] = None
    price: Optional[str] = None

def fetch_product_data_by_asin(asin: str) -> AmazonProductData:
    """
    TODO: Implement with Amazon Creators API (preferred).
    For now this is a stub so your Django wiring is done correctly.
    """
    # 1) Call Amazon API with asin
    # 2) Parse response
    # 3) Return AmazonProductData(image_url=..., title=..., price=...)
    return AmazonProductData(image_url=None)
