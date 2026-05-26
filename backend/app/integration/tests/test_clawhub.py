"""Unit tests for ClawHub Integration

Test the ClawHubIntegration class:
- Auto-register user
- Revoke credentials
- Generate login token
- Get iframe URL
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.integration.clawhub import ClawHubIntegration


@pytest.fixture
def clawhub_config():
    """ClawHub configuration"""
    return {
        "base_url": "https://clawhub.example.com",
        "api_key": "test_api_key_123"
    }


@pytest.fixture
def clawhub_integration(clawhub_config):
    """Create ClawHub integration instance"""
    return ClawHubIntegration(clawhub_config)


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_auto_register_user_success(clawhub_integration, mock_db):
    """Test successful user auto-registration"""
    # Mock httpx client
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "user_id": "clawhub_user_123",
        "api_key": "user_api_key_456"
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        # Mock DAO
        from backend.app.integration.crud import crud_integration_credentials
        original_create = crud_integration_credentials.integration_credentials_dao.create
        crud_integration_credentials.integration_credentials_dao.create = AsyncMock(return_value=MagicMock())

        try:
            result = await clawhub_integration.auto_register_user(
                db=mock_db,
                user_id=1,
                username="testuser",
                email="test@example.com"
            )

            # Verify result
            assert result["success"] is True
            assert result["user_id"] == "clawhub_user_123"
            assert result["api_key"] == "user_api_key_456"

            # Verify DAO was called
            crud_integration_credentials.integration_credentials_dao.create.assert_called_once()
        finally:
            crud_integration_credentials.integration_credentials_dao.create = original_create


@pytest.mark.asyncio
async def test_revoke_credentials_success(clawhub_integration, mock_db):
    """Test successful credential revocation"""
    # Mock get credentials
    mock_cred = MagicMock()
    mock_cred.credentials = {"api_key": "user_api_key_456"}

    from backend.app.integration.crud import crud_integration_credentials
    original_get = crud_integration_credentials.integration_credentials_dao.get_by_user_and_app
    original_update = crud_integration_credentials.integration_credentials_dao.update

    crud_integration_credentials.integration_credentials_dao.get_by_user_and_app = AsyncMock(return_value=mock_cred)
    crud_integration_credentials.integration_credentials_dao.update = AsyncMock(return_value=True)

    try:
        result = await clawhub_integration.revoke_credentials(
            db=mock_db,
            user_id=1
        )

        # Verify
        assert result is True
        crud_integration_credentials.integration_credentials_dao.update.assert_called_once()
    finally:
        crud_integration_credentials.integration_credentials_dao.get_by_user_and_app = original_get
        crud_integration_credentials.integration_credentials_dao.update = original_update


@pytest.mark.asyncio
async def test_revoke_credentials_not_found(clawhub_integration, mock_db):
    """Test revoking credentials when none exist"""
    from backend.app.integration.crud import crud_integration_credentials

    original_get = crud_integration_credentials.integration_credentials_dao.get_by_user_and_app
    crud_integration_credentials.integration_credentials_dao.get_by_user_and_app = AsyncMock(return_value=None)

    try:
        result = await clawhub_integration.revoke_credentials(
            db=mock_db,
            user_id=1
        )

        # Should return False when no credentials found
        assert result is False
    finally:
        crud_integration_credentials.integration_credentials_dao.get_by_user_and_app = original_get


@pytest.mark.asyncio
async def test_generate_login_token_success(clawhub_integration, mock_db):
    """Test successful login token generation"""
    # Mock get credentials
    mock_cred = MagicMock()
    mock_cred.credentials = {"api_key": "user_api_key_456"}

    from backend.app.integration.crud import crud_integration_credentials
    original_get = crud_integration_credentials.integration_credentials_dao.get_by_user_and_app

    crud_integration_credentials.integration_credentials_dao.get_by_user_and_app = AsyncMock(return_value=mock_cred)

    # Mock httpx client
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "token": "login_token_789",
        "expires_in": 300
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        try:
            token = await clawhub_integration.generate_login_token(
                db=mock_db,
                user_id=1
            )

            # Verify
            assert token == "login_token_789"
        finally:
            crud_integration_credentials.integration_credentials_dao.get_by_user_and_app = original_get


@pytest.mark.asyncio
async def test_generate_login_token_no_credentials(clawhub_integration, mock_db):
    """Test login token generation when no credentials exist"""
    from fastapi import HTTPException
    from backend.app.integration.crud import crud_integration_credentials

    original_get = crud_integration_credentials.integration_credentials_dao.get_by_user_and_app
    crud_integration_credentials.integration_credentials_dao.get_by_user_and_app = AsyncMock(return_value=None)

    try:
        with pytest.raises(HTTPException) as exc_info:
            await clawhub_integration.generate_login_token(
                db=mock_db,
                user_id=1
            )

        assert exc_info.value.status_code == 404
    finally:
        crud_integration_credentials.integration_credentials_dao.get_by_user_and_app = original_get


def test_get_iframe_url(clawhub_integration):
    """Test iframe URL generation"""
    token = "test_token_123"
    iframe_url = clawhub_integration.get_iframe_url(token)

    # Verify URL format
    assert iframe_url.startswith("https://clawhub.example.com")
    assert f"token={token}" in iframe_url


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
