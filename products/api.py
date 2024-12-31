from django.shortcuts import get_object_or_404
from ninja import Router
from django.conf import settings
from ninja_jwt.authentication import JWTAuth
from django.db.models import Q, Sum, Count
from orders.models import Order
from datetime import datetime, timedelta

from products.schemas import CategoryCreateSchema, CategorySchema, OfferCreateSchema, ProductSchema
from .models import Category, Offer, Product
from pydantic import BaseModel, Field
from typing import List, Optional

# router = Router(auth=JWTAuth())
router = Router()
public_offers = Router()



# Add a new product
@router.post("/add/")
def add_product(request, data: ProductSchema):
    # Ensure the user has permission to add products
    if request.auth.role not in ["farmer", "supplier"]:
        return {"error": "You are not allowed to add products"}
    product = Product.objects.create(
        seller=request.auth,
        name=data.name,
        description=data.description,
        category=data.category,
        price=data.price,
        stock=data.stock,
        tags=data.tags,
    )
    return {"message": "Product added successfully", "id": product.id}

# List all products with filtering and pagination
@router.get("/")
def list_products(
    request,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    tags: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    products = Product.objects.all()

    # Apply filters
    if category:
        products = products.filter(category__iexact=category)
    if min_price is not None:
        products = products.filter(price__gte=min_price)
    if max_price is not None:
        products = products.filter(price__lte=max_price)
    if tags:
        tag_list = tags.split(",")
        products = products.filter(tags__icontains=tag_list)

    total_count = products.count()
    products = products[offset:offset + limit]

    return {
        "total_count": total_count,
        "products": list(products.values("id", "name", "price", "stock", "category", "tags"))
    }

# Sales analytics
@router.get("/analytics/")
def get_sales_analytics(request):
    user = request.auth
    if user.role in ["farmer", "supplier"]:
        # Sales count
        sales = Order.objects.filter(product__seller=user).count()

        # Total revenue
        revenue = Order.objects.filter(product__seller=user).aggregate(
            total=Sum("total_price")
        )["total"] or 0

        # Recent sales trends (last 7 days)
        recent_sales = (
            Order.objects.filter(product__seller=user, created_at__gte=datetime.now() - timedelta(days=7))
            .values("created_at__date")
            .annotate(daily_sales=Count("id"), daily_revenue=Sum("total_price"))
            .order_by("created_at__date")
        )

        return {
            "sales_count": sales,
            "total_revenue": revenue,
            "recent_sales": list(recent_sales),
        }
    return {"error": "Analytics not available for this role"}



@public_offers.get("/offers/")
def list_offers(
    request,
    offer_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    category: Optional[str] = None,  # New filter for category
    limit: int = 10,
    offset: int = 0,
):
    offers = Offer.objects.filter(is_active=True, expires_at__gte=datetime.now())

    # Apply filters
    if offer_type:
        offers = offers.filter(offer_type__iexact=offer_type)
    if min_price is not None:
        offers = offers.filter(price_per_unit__gte=min_price)
    if max_price is not None:
        offers = offers.filter(price_per_unit__lte=max_price)
    if category:
        offers = offers.filter(product__category__name__iexact=category)

    total_count = offers.count()
    offers = offers[offset:offset + limit]

    # Construct image URLs and include them in the response
    host = request.build_absolute_uri('/')[:-1]  # Base URL without trailing slash
    offer_list = []
    for offer in offers:
        offer_data = {
            "id": offer.id,
            "product__name": offer.product.name,
            "price_per_unit": offer.price_per_unit,
            "quantity": offer.quantity,
            "offer_type": offer.offer_type,
            "expires_at": offer.expires_at,
            "product__category__name": offer.product.category.name,
            "product__image": f"{host}{offer.product.image.url}" if offer.product.image else None,
        }
        offer_list.append(offer_data)

    return {
        "total_count": total_count,
        "offers": offer_list,
    }



@public_offers.get("/offers/{id}/")
def get_offer(request, id: int):
    """
    Get details of a single offer by ID.
    """
    offer = get_object_or_404(
        Offer.objects.select_related("product__category"),
        id=id,
        is_active=True,
        expires_at__gte=datetime.now()
    )

    return {
        "id": offer.id,
        "product__name": offer.product.name,
        "price_per_unit": offer.price_per_unit,
        "quantity": offer.quantity,
        "category": offer.product.category.name,
        "expires_at": offer.expires_at,
        "image_url": request.build_absolute_uri(offer.product.image.url)
        if offer.product.image
        else None,
    }


# Authenticated user's "My Offers" endpoint
@router.get("/my/offers/")
def my_offers(request, limit: int = 10, offset: int = 0):
    user = request.auth
    offers = Offer.objects.filter(created_by=user)

    total_count = offers.count()
    offers = offers[offset:offset + limit]

    return {
        "total_count": total_count,
        "offers": list(offers.values(
            "id", "product__name", "price_per_unit", "quantity", "offer_type", "expires_at", "is_active"
        ))
    }




# Create an offer
@router.post("/offer/create/")
def create_offer(request, data: OfferCreateSchema):
    product = Product.objects.get(id=data.product_id)

    # Check permissions and stock for sell offers
    if data.offer_type == "Sell":
        if request.auth.role not in ["farmer", "supplier"]:
            return {"error": "Only farmers and suppliers can create sell offers"}
        if product.stock < data.quantity:
            return {"error": "Not enough stock to create the sell offer"}

    # Create the offer
    offer = Offer.objects.create(
        product=product,
        offer_type=data.offer_type,
        price_per_unit=data.price_per_unit,
        quantity=data.quantity,
        min_order=data.min_order,
        max_order=data.max_order,
        created_by=request.auth,
        expires_at=datetime.now() + timedelta(days=data.validity_days),
    )

    # Deduct stock for sell offers
    if data.offer_type == "Sell":
        product.stock -= data.quantity
        product.save()
    return {"message": "Offer created successfully", "id": offer.id}



# Search offers
@router.get("/offers/search/")
def search_offers(
    request,
    query: Optional[str] = None,
    offer_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 10,
    offset: int = 0,
):
    offers = Offer.objects.filter(is_active=True)

    # Apply filters
    if query:
        offers = offers.filter(
            Q(product__name__icontains=query) | Q(product__description__icontains=query)
        )
    if offer_type:
        offers = offers.filter(offer_type__iexact=offer_type)
    if min_price is not None:
        offers = offers.filter(price_per_unit__gte=min_price)
    if max_price is not None:
        offers = offers.filter(price_per_unit__lte=max_price)

    total_count = offers.count()
    offers = offers[offset:offset + limit]

    return {
        "total_count": total_count,
        "offers": list(offers.values(
            "id", "product__name", "price_per_unit", "quantity", "offer_type", "expires_at"
        ))
    }




# Get all categories
@public_offers.get("/categories/", response=List[CategorySchema])
def list_categories(request):
    """List all categories."""
    categories = Category.objects.all()
    return categories 

# Create a category
@router.post("/categories/", response=CategorySchema)
def create_category(request, data: CategoryCreateSchema):
    """Create a new category."""
    category = Category.objects.create(**data.dict())
    return category

# Get a single category
@router.get("/categories/{category_id}/", response=CategorySchema)
def get_category(request, category_id: int):
    """Retrieve a specific category by ID."""
    category = get_object_or_404(Category, id=category_id)
    return category

# Delete a category
@router.delete("/categories/{category_id}/", response={})
def delete_category(request, category_id: int):
    """Delete a specific category by ID."""
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return {"success": True}