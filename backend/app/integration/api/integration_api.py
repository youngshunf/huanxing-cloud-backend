"""
Third-party application integration API routes
"""
from fastapi import APIRouter, HTTPException, Request

from backend.app.integration.registry import registry
from backend.app.integration.clawhub import ClawHubIntegration
from backend.app.integration.crud.crud_integration_credentials import integration_credentials_dao
from backend.common.response.response_schema import ResponseModel, response_base
from backend.database.db import CurrentSession
from backend.common.security.jwt import DependsJwtAuth

# Register ClawHub integration
registry.register("clawhub", ClawHubIntegration)

router = APIRouter()


@router.post(
    "/{app_id}/connect",
    summary="Connect to third-party app",
    description="Auto-register user to third-party app and save credentials",
    dependencies=[DependsJwtAuth]
)
async def connect_app(
    app_id: str,
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    """
    Connect to third-party application

    Auto-register user to third-party platform (e.g., ClawHub)
    """
    try:
        # Get integration instance
        integration = await registry.get(db, app_id)

        # Auto-register user
        credentials = await integration.auto_register_user(
            db=db,
            user_id=request.user.id,
            username=request.user.username,
            email=getattr(request.user, "email", None),
        )

        return response_base.success(data={
            "app_id": app_id,
            "connected": True,
            "credentials": credentials,
        })

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")


@router.post(
    "/{app_id}/disconnect",
    summary="Disconnect from third-party app",
    description="Revoke user credentials and disconnect",
    dependencies=[DependsJwtAuth]
)
async def disconnect_app(
    app_id: str,
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    """
    Disconnect from third-party application
    """
    try:
        # Get integration instance
        integration = await registry.get(db, app_id)

        # Revoke credentials
        success = await integration.revoke_credentials(
            db=db,
            user_id=request.user.id,
        )

        return response_base.success(data={
            "app_id": app_id,
            "disconnected": success,
        })

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Disconnection failed: {str(e)}")


@router.get(
    "/{app_id}/status",
    summary="Get connection status",
    description="Check if user is connected to third-party app",
    dependencies=[DependsJwtAuth]
)
async def get_connection_status(
    app_id: str,
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    """
    Get connection status
    """
    try:
        # Query credentials
        cred = await integration_credentials_dao.get_by_user_and_app(
            db, request.user.id, app_id
        )

        if not cred or not cred.is_active:
            return response_base.success(data={
                "app_id": app_id,
                "connected": False,
            })

        return response_base.success(data={
            "app_id": app_id,
            "connected": True,
            "created_time": cred.created_time.isoformat() if cred.created_time else None,
            "expires_at": cred.expires_at.isoformat() if cred.expires_at else None,
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get(
    "/{app_id}/iframe-url",
    summary="Get iframe embed URL",
    description="Generate iframe URL with auto-login token",
    dependencies=[DependsJwtAuth]
)
async def get_iframe_url(
    app_id: str,
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    """
    Get iframe embed URL

    Used to embed third-party app pages in WebUI with auto-login
    """
    try:
        # Get integration instance
        integration = await registry.get(db, app_id)

        # Generate login token
        login_token = await integration.generate_login_token(
            db=db,
            user_id=request.user.id,
        )

        # Get iframe URL
        iframe_url = integration.get_iframe_url(login_token)

        return response_base.success(data={
            "app_id": app_id,
            "iframe_url": iframe_url,
            "login_token": login_token,
        })

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")


@router.get(
    "/apps/list",
    summary="Get available apps list",
    description="List all enabled third-party apps"
)
async def list_available_apps(
    db: CurrentSession,
) -> ResponseModel:
    """
    Get available apps list
    """
    from backend.app.integration.crud.crud_integration_apps import integration_apps_dao

    try:
        # Query all enabled apps
        apps = await integration_apps_dao.get_all(db)
        enabled_apps = [
            {
                "app_id": app.app_id,
                "app_name": app.app_name,
                "app_type": app.app_type,
                "description": app.description,
                "icon_url": app.icon_url,
                "is_enabled": app.is_enabled,
            }
            for app in apps
            if app.is_enabled
        ]

        return response_base.success(data={
            "apps": enabled_apps,
            "total": len(enabled_apps),
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list apps: {str(e)}")
