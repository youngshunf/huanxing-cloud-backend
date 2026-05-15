import asyncio
import asyncpg
from backend.core.conf import settings

async def rename_columns():
    conn = await asyncpg.connect(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        database=settings.DATABASE_SCHEMA,
    )
    
    tables = [
        'app_permission_grants',
        'app_dynamic_permission_requests',
        'app_scopes',
        'app_developers',
        'app_manifests',
        'app_versions',
        'app_listings',
        'app_installations',
        'app_tools',
        'app_resources',
        'app_events',
        'app_reviews',
        'app_entitlements',
        'app_agent_bindings',
        'app_data_records',
        'app_permission_audit_logs',
    ]
    
    for table in tables:
        try:
            await conn.execute(f'ALTER TABLE {table} RENAME COLUMN created_at TO created_time')
            print(f'✓ {table}.created_at -> created_time')
        except Exception as e:
            if 'does not exist' not in str(e):
                print(f'✗ {table}.created_at: {e}')
        
        try:
            await conn.execute(f'ALTER TABLE {table} RENAME COLUMN updated_at TO updated_time')
            print(f'✓ {table}.updated_at -> updated_time')
        except Exception as e:
            if 'does not exist' not in str(e):
                print(f'✗ {table}.updated_at: {e}')
    
    await conn.close()
    print('\n所有列重命名完成')

if __name__ == '__main__':
    asyncio.run(rename_columns())
