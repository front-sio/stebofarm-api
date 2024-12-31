from ninja import Router
from .models import Notification

router = Router(auth=JWTAuth())

@router.get("/")
def list_notifications(request):
    notifications = Notification.objects.filter(recipient=request.auth, is_read=False)
    return notifications.values()

@router.post("/{notification_id}/read/")
def mark_as_read(request, notification_id: int):
    notification = Notification.objects.get(id=notification_id, recipient=request.auth)
    notification.is_read = True
    notification.save()
    return {"message": "Notification marked as read"}
