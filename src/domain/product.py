"""
Domain entity definitions for products to be indexed in Qdrant.

The `Product` model follows the contract below and is ready for
( de )‑serialization with Pydantic while remaining agnostic to any
specific persistence layer.
"""

from uuid import UUID, uuid4
from typing import Optional, List
from pydantic import (
    BaseModel,
    HttpUrl,
    Field,
    PositiveFloat,
    NonNegativeInt,
    NonNegativeFloat,
)


class Vector(BaseModel):
    product_details_vector: List[float]


class Merchant(BaseModel):
    name: str
    link: HttpUrl


class Payload(BaseModel):
    description: Optional[str] = None
    merchant: Merchant
    price: PositiveFloat
    product_details: Optional[str] = None
    product_link: HttpUrl
    product_name: str
    reviews_count: NonNegativeInt
    reviews_score: NonNegativeFloat
    search_keyword: Optional[str] = None
    without_discount_price: Optional[PositiveFloat] = None


class Product(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    payload: Payload
    vector: Optional[Vector] = None


__all__ = ("Product", "Payload", "Merchant", "Vector")
