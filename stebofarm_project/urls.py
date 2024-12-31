from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from ninja import NinjaAPI

from users.api import router as users_router
from users.api import public_router as public_router
from products.api import router as products_router
from products.api import public_offers as public_offers
from community.api import router as community_router

api = NinjaAPI()
api.add_router("/public/", public_router)
api.add_router("/users/", users_router)
api.add_router("/products/", products_router)
api.add_router("/public_offers/", public_offers)
api.add_router("/community/", community_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
