"""Webhook endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.dependencies import get_current_active_user
from app.core.security import generate_api_key
from app.models.user import User
from app.models.webhook import Webhook, WebhookEvent
from app.schemas.webhook import WebhookCreate, WebhookUpdate, WebhookResponse, WebhookEventResponse

router = APIRouter()


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new webhook"""
    # Generate webhook secret
    secret = generate_api_key()

    new_webhook = Webhook(
        **webhook_data.model_dump(),
        user_id=current_user.id,
        secret=secret
    )

    db.add(new_webhook)
    await db.commit()
    await db.refresh(new_webhook)

    return new_webhook


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's webhooks"""
    result = await db.execute(
        select(Webhook).where(Webhook.user_id == current_user.id)
    )
    webhooks = result.scalars().all()

    return webhooks


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get webhook details"""
    result = await db.execute(
        select(Webhook).where(Webhook.id == webhook_id, Webhook.user_id == current_user.id)
    )
    webhook = result.scalar_one_or_none()

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )

    return webhook


@router.patch("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: int,
    webhook_data: WebhookUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update webhook"""
    result = await db.execute(
        select(Webhook).where(Webhook.id == webhook_id, Webhook.user_id == current_user.id)
    )
    webhook = result.scalar_one_or_none()

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )

    # Update webhook
    for field, value in webhook_data.model_dump(exclude_unset=True).items():
        setattr(webhook, field, value)

    await db.commit()
    await db.refresh(webhook)

    return webhook


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete webhook"""
    result = await db.execute(
        select(Webhook).where(Webhook.id == webhook_id, Webhook.user_id == current_user.id)
    )
    webhook = result.scalar_one_or_none()

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )

    await db.delete(webhook)
    await db.commit()

    return None


@router.get("/{webhook_id}/events", response_model=List[WebhookEventResponse])
async def list_webhook_events(
    webhook_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List webhook events/deliveries"""
    # Verify webhook ownership
    result = await db.execute(
        select(Webhook).where(Webhook.id == webhook_id, Webhook.user_id == current_user.id)
    )
    webhook = result.scalar_one_or_none()

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )

    # Get events
    result = await db.execute(
        select(WebhookEvent).where(WebhookEvent.webhook_id == webhook_id).limit(100)
    )
    events = result.scalars().all()

    return events


@router.post("/{webhook_id}/test", response_model=WebhookEventResponse)
async def test_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Test webhook by sending a test event"""
    result = await db.execute(
        select(Webhook).where(Webhook.id == webhook_id, Webhook.user_id == current_user.id)
    )
    webhook = result.scalar_one_or_none()

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )

    # Create test event
    from app.models.webhook import WebhookEventType
    from datetime import datetime

    test_event = WebhookEvent(
        webhook_id=webhook.id,
        event_type=WebhookEventType.INVESTIGATION_CREATED,
        payload={
            "event": "test",
            "message": "This is a test webhook event",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    db.add(test_event)
    await db.commit()
    await db.refresh(test_event)

    # TODO: Trigger actual webhook delivery via Celery

    return test_event
