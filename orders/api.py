from ninja import Router
from ninja_jwt.authentication import JWTAuth
from django.db import transaction
from datetime import datetime
from .models import Order
from products.models import Offer
from pydantic import BaseModel

router = Router(auth=JWTAuth())

# Schema for creating an order
class OrderSchema(BaseModel):
    offer_id: int
    quantity: int

# Create an order for an offer
@router.post("/create/")
def create_order(request, data: OrderSchema):
    try:
        offer = Offer.objects.get(id=data.offer_id, is_active=True)

        # Check if sufficient quantity is available in the offer
        if offer.quantity < data.quantity:
            return {"error": "Not enough quantity available in the offer"}

        total_price = data.quantity * offer.price_per_unit

        with transaction.atomic():
            # Create the order
            order = Order.objects.create(
                buyer=request.auth,
                offer=offer,
                quantity=data.quantity,
                total_price=total_price,
                status="Pending",
            )

            # Deduct quantity from the offer
            offer.quantity -= data.quantity
            if offer.quantity == 0:
                offer.is_active = False
            offer.save()

        return {
            "order_id": order.id,
            "status": order.status,
            "total_price": total_price,
            "offer": offer.product.name,
        }
    except Offer.DoesNotExist:
        return {"error": "Offer not found or no longer active"}

# List all orders for the authenticated user
@router.get("/list/")
def list_orders(request):
    user = request.auth
    orders = Order.objects.filter(buyer=user).values(
        "id",
        "offer__product__name",
        "quantity",
        "total_price",
        "status",
        "created_at",
    )
    return {"orders": list(orders)}

# Cancel an order
@router.post("/cancel/{order_id}/")
def cancel_order(request, order_id: int):
    try:
        order = Order.objects.get(id=order_id, buyer=request.auth)
        if order.status == "Pending":
            with transaction.atomic():
                # Restore the offer quantity
                offer = order.offer
                offer.quantity += order.quantity
                offer.is_active = True
                offer.save()

                # Update order status
                order.status = "Cancelled"
                order.save()

            return {"message": "Order cancelled successfully", "order_id": order.id}
        else:
            return {"error": "Only pending orders can be cancelled"}
    except Order.DoesNotExist:
        return {"error": "Order not found"}

# View a specific order's details
@router.get("/{order_id}/")
def get_order_details(request, order_id: int):
    try:
        order = Order.objects.get(id=order_id, buyer=request.auth)
        return {
            "order_id": order.id,
            "offer": order.offer.product.name,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "status": order.status,
            "created_at": order.created_at,
        }
    except Order.DoesNotExist:
        return {"error": "Order not found"}

# Complete an order
@router.post("/{order_id}/complete/")
def complete_order(request, order_id: int):
    try:
        order = Order.objects.get(id=order_id, buyer=request.auth)
        if order.status == "Pending":
            order.status = "Completed"
            order.save()
            return {"message": "Order completed successfully", "order_id": order.id}
        return {"error": "Order cannot be marked as completed"}
    except Order.DoesNotExist:
        return {"error": "Order not found"}
