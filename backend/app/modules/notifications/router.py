from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import CurrentUser, get_current_user
from app.modules.notifications import service
from app.modules.notifications.schemas import NotificationOut, UnreadCountOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_my_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: CurrentUser = Depends(get_current_user),
):
    return service.list_notifications(user.id, unread_only, limit, offset)


@router.get("/unread-count", response_model=UnreadCountOut)
def unread_count(user: CurrentUser = Depends(get_current_user)):
    return UnreadCountOut(count=service.count_unread(user.id))


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_read(
    notification_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    n = service.mark_read(user.id, notification_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    return n


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_read(user: CurrentUser = Depends(get_current_user)):
    service.mark_all_read(user.id)