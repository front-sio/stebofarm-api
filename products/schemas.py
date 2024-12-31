from ninja import ModelSchema
from pydantic import BaseModel, Field
from typing import List, Optional

from products.models import Category


class CategorySchema(ModelSchema):
    class Config:
        model = Category  # Link the schema to the model
        model_fields = ['id', 'name'] 




class CategoryCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None

class ProductSchema(BaseModel):
    id: int
    name: str
    description: str
    category: CategorySchema
    price: float
    stock: int
    image: Optional[str] = None
    seller: int  # ID of the seller
    tags: Optional[str] = None
    created_at: str

    

class OfferCreateSchema(BaseModel):
    product_id: int
    offer_type: str = Field(..., description="Offer type ('Buy' or 'Sell')")
    price_per_unit: float = Field(..., ge=0, description="Price per unit")
    quantity: int = Field(..., ge=1, description="Quantity for the offer")
    min_order: int = Field(..., ge=1, description="Minimum order quantity")
    max_order: int = Field(..., ge=1, description="Maximum order quantity")
    validity_days: int = Field(default=7, description="Validity in days")
