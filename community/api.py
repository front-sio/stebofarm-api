from ninja import Router
from ninja_jwt.authentication import JWTAuth
from .models import Community

router = Router(auth=JWTAuth())

@router.get("/")
def list_communities(request):
    return Community.objects.all().values("id", "name", "description")
