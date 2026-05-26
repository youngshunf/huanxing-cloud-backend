"""
GitHub Webhook API for Marketplace

Receives GitHub push events and triggers sync for skills and apps.
"""
import hashlib
import hmac
from typing import Any

from fastapi import APIRouter, Request, Header, HTTPException
from pydantic import BaseModel

from backend.app.marketplace.service.github_sync_service import github_sync_service
from backend.app.marketplace.service.github_app_sync_service import github_app_sync_service
from backend.common.log import log
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.core.conf import settings
from backend.database.db import CurrentSession

router = APIRouter()


class WebhookResponse(BaseModel):
    """Webhook response"""
    message: str
    synced: int = 0
    failed: int = 0


def verify_github_signature(payload: bytes, signature: str) -> bool:
    """
    Verify GitHub webhook signature

    Args:
        payload: Request body
        signature: X-Hub-Signature-256 header value

    Returns:
        True if signature is valid
    """
    if not signature:
        return False

    # Get webhook secret from settings
    secret = getattr(settings, 'GITHUB_WEBHOOK_SECRET', '')
    if not secret:
        log.warning("GITHUB_WEBHOOK_SECRET not configured, skipping signature verification")
        return True  # Allow if secret not configured (for development)

    # Signature format: sha256=<hash>
    if not signature.startswith('sha256='):
        return False

    expected_signature = signature[7:]  # Remove 'sha256=' prefix

    # Calculate HMAC
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    calculated_signature = mac.hexdigest()

    return hmac.compare_digest(calculated_signature, expected_signature)


@router.post(
    '/github/skills',
    summary='GitHub Webhook for Skills',
    description='Receives GitHub push events and triggers skill sync',
)
async def github_webhook_skills(
    request: Request,
    db: CurrentSession,
    x_hub_signature_256: str | None = Header(None, alias='X-Hub-Signature-256'),
    x_github_event: str | None = Header(None, alias='X-GitHub-Event'),
) -> ResponseSchemaModel[WebhookResponse]:
    """
    GitHub webhook endpoint for skills

    Triggered when huanxing-hub repository receives a push event
    """
    try:
        # Read request body
        body = await request.body()

        # Verify signature
        if not verify_github_signature(body, x_hub_signature_256 or ''):
            log.error("Invalid GitHub webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse payload
        payload = await request.json()

        # Only handle push events
        if x_github_event != 'push':
            log.info(f"Ignoring GitHub event: {x_github_event}")
            return response_base.success(data=WebhookResponse(
                message=f"Ignored event: {x_github_event}"
            ))

        # Check if skills directory was modified
        commits = payload.get('commits', [])
        has_skill_changes = False

        for commit in commits:
            modified = commit.get('modified', []) + commit.get('added', []) + commit.get('removed', [])
            if any(f.startswith('skills/') for f in modified):
                has_skill_changes = True
                break

        if not has_skill_changes:
            log.info("No skill changes detected, skipping sync")
            return response_base.success(data=WebhookResponse(
                message="No skill changes detected"
            ))

        # Trigger sync
        log.info("Triggering skill sync from GitHub webhook")
        result = await github_sync_service.sync_from_github(db, force=True)

        if result.get('success'):
            return response_base.success(data=WebhookResponse(
                message="Skill sync completed",
                synced=result.get('synced', 0),
                failed=result.get('failed', 0)
            ))
        else:
            return response_base.fail(message=f"Skill sync failed: {result.get('error')}")

    except Exception as e:
        log.error(f"GitHub webhook error: {e}")
        return response_base.fail(message=str(e))


@router.post(
    '/github/apps',
    summary='GitHub Webhook for Apps',
    description='Receives GitHub push events and triggers app template sync',
)
async def github_webhook_apps(
    request: Request,
    db: CurrentSession,
    x_hub_signature_256: str | None = Header(None, alias='X-Hub-Signature-256'),
    x_github_event: str | None = Header(None, alias='X-GitHub-Event'),
) -> ResponseSchemaModel[WebhookResponse]:
    """
    GitHub webhook endpoint for app templates

    Triggered when huanxing-hub repository receives a push event
    """
    try:
        # Read request body
        body = await request.body()

        # Verify signature
        if not verify_github_signature(body, x_hub_signature_256 or ''):
            log.error("Invalid GitHub webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse payload
        payload = await request.json()

        # Only handle push events
        if x_github_event != 'push':
            log.info(f"Ignoring GitHub event: {x_github_event}")
            return response_base.success(data=WebhookResponse(
                message=f"Ignored event: {x_github_event}"
            ))

        # Check if templates directory was modified
        commits = payload.get('commits', [])
        has_template_changes = False

        for commit in commits:
            modified = commit.get('modified', []) + commit.get('added', []) + commit.get('removed', [])
            if any(f.startswith('templates/') and not f.startswith('templates/_') for f in modified):
                has_template_changes = True
                break

        if not has_template_changes:
            log.info("No template changes detected, skipping sync")
            return response_base.success(data=WebhookResponse(
                message="No template changes detected"
            ))

        # Trigger sync
        log.info("Triggering app template sync from GitHub webhook")
        result = await github_app_sync_service.sync_from_github(db, force=True)

        if result.get('success'):
            return response_base.success(data=WebhookResponse(
                message="App template sync completed",
                synced=result.get('synced', 0),
                failed=result.get('failed', 0)
            ))
        else:
            return response_base.fail(message=f"App template sync failed: {result.get('error')}")

    except Exception as e:
        log.error(f"GitHub webhook error: {e}")
        return response_base.fail(message=str(e))
