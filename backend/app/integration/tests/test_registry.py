"""Unit tests for Integration Registry

Test the IntegrationRegistry class:
- Register integration classes
- Get integration instances
- Handle errors for unregistered apps
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.integration.registry import IntegrationRegistry
from backend.app.integration.base import BaseIntegration


class MockIntegration(BaseIntegration):
    """Mock integration for testing"""

    async def auto_register_user(self, db: AsyncSession, user_id: int, username: str, email: str = None):
        return {"user_id": user_id, "registered": True}

    async def revoke_credentials(self, db: AsyncSession, user_id: int):
        return True

    async def generate_login_token(self, db: AsyncSession, user_id: int):
        return "mock_token_123"

    def get_iframe_url(self, login_token: str):
        return f"https://mock.example.com/login?token={login_token}"


@pytest.fixture
def registry():
    """Create a fresh registry for each test"""
    return IntegrationRegistry()


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return AsyncMock(spec=AsyncSession)


def test_register_integration(registry):
    """Test registering an integration class"""
    registry.register("mock_app", MockIntegration)
    assert "mock_app" in registry._integration_classes
    assert registry._integration_classes["mock_app"] == MockIntegration


def test_register_multiple_integrations(registry):
    """Test registering multiple integration classes"""
    registry.register("app1", MockIntegration)
    registry.register("app2", MockIntegration)

    assert len(registry._integration_classes) == 2
    assert "app1" in registry._integration_classes
    assert "app2" in registry._integration_classes


@pytest.mark.asyncio
async def test_get_integration_success(registry, mock_db):
    """Test getting an integration instance successfully"""
    # Register the integration
    registry.register("mock_app", MockIntegration)

    # Mock the database query
    mock_app = MagicMock()
    mock_app.app_id = "mock_app"
    mock_app.app_type = "mock_app"
    mock_app.is_enabled = True
    mock_app.config = {"base_url": "https://mock.example.com"}

    # Mock the DAO
    from backend.app.integration.crud import crud_integration_apps
    original_get = crud_integration_apps.integration_apps_dao.get_by_app_id
    crud_integration_apps.integration_apps_dao.get_by_app_id = AsyncMock(return_value=mock_app)

    try:
        # Get the integration
        integration = await registry.get(mock_db, "mock_app")

        # Verify
        assert isinstance(integration, MockIntegration)
        assert integration.config == {"base_url": "https://mock.example.com"}
    finally:
        # Restore original method
        crud_integration_apps.integration_apps_dao.get_by_app_id = original_get


@pytest.mark.asyncio
async def test_get_integration_not_found(registry, mock_db):
    """Test getting an integration that doesn't exist in database"""
    from fastapi import HTTPException
    from backend.app.integration.crud import crud_integration_apps

    # Mock the DAO to return None
    original_get = crud_integration_apps.integration_apps_dao.get_by_app_id
    crud_integration_apps.integration_apps_dao.get_by_app_id = AsyncMock(return_value=None)

    try:
        with pytest.raises(HTTPException) as exc_info:
            await registry.get(mock_db, "nonexistent_app")

        assert exc_info.value.status_code == 404
    finally:
        crud_integration_apps.integration_apps_dao.get_by_app_id = original_get


@pytest.mark.asyncio
async def test_get_integration_disabled(registry, mock_db):
    """Test getting a disabled integration"""
    from fastapi import HTTPException
    from backend.app.integration.crud import crud_integration_apps

    # Mock the database query
    mock_app = MagicMock()
    mock_app.app_id = "disabled_app"
    mock_app.is_enabled = False

    original_get = crud_integration_apps.integration_apps_dao.get_by_app_id
    crud_integration_apps.integration_apps_dao.get_by_app_id = AsyncMock(return_value=mock_app)

    try:
        with pytest.raises(HTTPException) as exc_info:
            await registry.get(mock_db, "disabled_app")

        assert exc_info.value.status_code == 404
    finally:
        crud_integration_apps.integration_apps_dao.get_by_app_id = original_get


@pytest.mark.asyncio
async def test_get_integration_unregistered_type(registry, mock_db):
    """Test getting an integration with unregistered type"""
    from fastapi import HTTPException
    from backend.app.integration.crud import crud_integration_apps

    # Mock the database query
    mock_app = MagicMock()
    mock_app.app_id = "unknown_app"
    mock_app.app_type = "unknown_type"
    mock_app.is_enabled = True

    original_get = crud_integration_apps.integration_apps_dao.get_by_app_id
    crud_integration_apps.integration_apps_dao.get_by_app_id = AsyncMock(return_value=mock_app)

    try:
        with pytest.raises(HTTPException) as exc_info:
            await registry.get(mock_db, "unknown_app")

        assert exc_info.value.status_code == 500
        assert "unregistered" in str(exc_info.value.detail).lower()
    finally:
        crud_integration_apps.integration_apps_dao.get_by_app_id = original_get


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
