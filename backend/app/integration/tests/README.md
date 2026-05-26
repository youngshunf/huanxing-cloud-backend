# Integration Module Tests

This directory contains tests for the third-party application integration system.

## Test Structure

```
tests/
├── __init__.py
├── test_registry.py      # Unit tests for IntegrationRegistry
├── test_clawhub.py       # Unit tests for ClawHubIntegration
└── README.md            # This file

/tests/
└── test_integration.py   # E2E test for complete integration flow
```

## Running Tests

### Unit Tests

Run all unit tests in the integration module:

```bash
cd /Users/mac/openclaw-workspace/huanxing/huanxing-project/huanxing-cloud-backend
pytest backend/app/integration/tests/ -v
```

Run specific test file:

```bash
pytest backend/app/integration/tests/test_registry.py -v
pytest backend/app/integration/tests/test_clawhub.py -v
```

### E2E Tests

The E2E test requires a running backend server and database.

1. Start the backend server:
```bash
cd /Users/mac/openclaw-workspace/huanxing/huanxing-project/huanxing-cloud-backend
# Start your backend server (e.g., uvicorn main:app)
```

2. Run the E2E test:
```bash
python tests/test_integration.py
```

## Test Coverage

### test_registry.py
- ✓ Register integration classes
- ✓ Register multiple integrations
- ✓ Get integration instance successfully
- ✓ Handle app not found error
- ✓ Handle disabled app error
- ✓ Handle unregistered app type error

### test_clawhub.py
- ✓ Auto-register user successfully
- ✓ Revoke credentials successfully
- ✓ Revoke credentials when none exist
- ✓ Generate login token successfully
- ✓ Generate login token with no credentials
- ✓ Get iframe URL

### test_integration.py (E2E)
- ✓ List available apps
- ✓ Check initial connection status
- ✓ Connect to ClawHub
- ✓ Verify connection status after connecting
- ✓ Get iframe URL with login token
- ✓ Disconnect from ClawHub
- ✓ Verify disconnection

## Prerequisites

Before running tests, ensure:

1. **Database Setup**: Integration tables must exist
   ```bash
   # Run migrations or execute SQL files
   psql -d your_database -f backend/sql/tables/integration_apps.sql
   psql -d your_database -f backend/sql/tables/integration_credentials.sql
   ```

2. **Test Data**: For E2E tests, insert a ClawHub app record
   ```sql
   INSERT INTO integration_apps (app_id, app_name, app_type, base_url, config, is_enabled)
   VALUES (
       'clawhub',
       'ClawHub',
       'clawhub',
       'https://clawhub.example.com',
       '{"api_key": "test_key"}',
       true
   );
   ```

3. **Dependencies**: Install test dependencies
   ```bash
   pip install pytest pytest-asyncio httpx
   ```

## Mocking Strategy

Unit tests use mocking to avoid external dependencies:
- Database queries are mocked using `AsyncMock`
- HTTP requests are mocked using `unittest.mock.patch`
- DAO methods are temporarily replaced during tests

E2E tests use real HTTP requests to test the complete flow.

## Adding New Tests

When adding a new integration type:

1. Create unit tests in `tests/test_<integration_name>.py`
2. Update E2E test to include the new integration
3. Update this README with test coverage

## Troubleshooting

**Import errors**: Ensure PYTHONPATH includes the backend directory
```bash
export PYTHONPATH=/Users/mac/openclaw-workspace/huanxing/huanxing-project/huanxing-cloud-backend:$PYTHONPATH
```

**Database connection errors**: Check database configuration in settings
```bash
# Verify database connection
psql -d your_database -c "SELECT 1"
```

**Authentication errors in E2E tests**: Ensure Redis is running for JWT token storage
```bash
redis-cli ping
```
