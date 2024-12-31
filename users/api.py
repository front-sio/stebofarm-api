import secrets
from pydantic import BaseModel
from django.contrib.auth import authenticate
from ninja_jwt.tokens import RefreshToken
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from typing import Optional
from .models import User, FrontendApp
from .schemas import FrontendAppSchema, LoginSchema, UserRegistrationSchema, UserProfileUpdateSchema

router = Router(auth=JWTAuth())
public_router = Router()

# Frontend Registration
@router.post("/register_frontend/")
def register_frontend(request, data: FrontendAppSchema):
    """Register a new frontend application."""
    name = data.name
    if not name:
        return {"error": "Frontend name is required"}

    # Generate a unique key for the frontend
    unique_key = secrets.token_hex(32)
    app, created = FrontendApp.objects.get_or_create(name=name, defaults={"unique_key": unique_key})

    if not created:
        return {"error": "Frontend with this name already exists"}

    return {"message": "Frontend registered successfully", "unique_key": unique_key}


# User Registration
@public_router.post("/register/")
def register_user(request, data: UserRegistrationSchema):
    if User.objects.filter(username=data.username).exists():
        return {"error": "Username already exists"}
    if User.objects.filter(email=data.email).exists():
        return {"error": "Email already exists"}
    if not data.national_id and not data.driving_license:
        return {"error": "Either National ID or Driving License must be provided"}
    if data.national_id and User.objects.filter(national_id=data.national_id).exists():
        return {"error": "National ID is already registered"}
    if data.driving_license and User.objects.filter(driving_license=data.driving_license).exists():
        return {"error": "Driving License is already registered"}

    user = User.objects.create_user(
        username=data.username,
        email=data.email,
        password=data.password,
        role=data.role,
        national_id=data.national_id,
        driving_license=data.driving_license,
    )
    user.is_verified = False
    user.save()

    return {"message": "User registered successfully. Verification pending.", "id": user.id}




@public_router.post("/login/")
def login_user(request, data: LoginSchema):
    """Authenticate user and return tokens along with user data."""
    user = authenticate(username=data.username, password=data.password)
    if not user:
        return {"error": "Invalid username or password"}  # Login fails if credentials are wrong

    # Generate JWT tokens for the user
    refresh = RefreshToken.for_user(user)

    # Return tokens and user details
    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,  # Assuming role field exists in the User model
            "is_verified": user.is_verified,
        },
    }

# User Profile
@router.get("/profile/")
def get_user_profile(request):
    user = request.auth
    return {
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "national_id": user.national_id,
        "driving_license": user.driving_license,
        "is_verified": user.is_verified,
        "location": user.profile.location,
        "contact_number": user.profile.contact_number,
    }

@router.put("/profile/")
def update_user_profile(request, data: UserProfileUpdateSchema):
    user = request.auth
    if data.location:
        user.profile.location = data.location
    if data.contact_number:
        user.profile.contact_number = data.contact_number
    user.save()
    return {"message": "Profile updated successfully"}

# Dashboard
@router.get("/dashboard/")
def get_dashboard(request):
    user = request.auth
    if not user.is_verified:
        return {"error": "User is not verified. Please complete verification."}

    if user.role == 'farmer':
        return {"role": "Farmer", "products_count": 10, "orders_count": 5}  # Example
    elif user.role == 'supplier':
        return {"role": "Supplier", "inventory_count": 8, "pending_orders_count": 2}  # Example
    elif user.role == 'expert':
        return {"role": "Expert", "pending_services_count": 4}  # Example
    else:
        return {"error": "Invalid role"}

# Admin Verification
@router.post("/verify/{user_id}/")
def verify_user(request, user_id: int):
    if not request.auth.is_superuser:
        return {"error": "Only administrators can verify users"}
    try:
        user = User.objects.get(id=user_id)
        if user.is_verified:
            return {"message": "User is already verified"}
        user.is_verified = True
        user.save()
        return {"message": "User verified successfully", "user_id": user.id}
    except User.DoesNotExist:
        return {"error": "User not found"}

# List Users
@router.get("/list/")
def list_users(request, role: Optional[str] = None):
    if not request.auth.is_superuser:
        return {"error": "Only admin users can access this"}
    users = User.objects.all()
    if role:
        users = users.filter(role=role)
    return {
        "total_users": users.count(),
        "users": list(users.values("id", "username", "email", "role", "is_verified")),
    }
