"""SDK 集成测试

测试数据客户端、审计客户端等功能。
"""
from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_data_records import app_data_records_dao
from backend.app.app_platform.model import AppDataRecords
from backend.app.app_platform.schema.app_data_records import CreateAppDataRecordsParam
from backend.app.app_platform.sdk.app_context import AppContext


@pytest.mark.asyncio
async def test_app_context_creation(
    test_owner_id: str,
    test_app_id: str,
):
    """测试应用上下文创建"""
    ctx = AppContext(
        owner_id=test_owner_id,
        app_id=test_app_id,
        installation_id='test_installation_001',
    )

    assert ctx.owner_id == test_owner_id
    assert ctx.app_id == test_app_id
    assert ctx.installation_id == 'test_installation_001'


@pytest.mark.asyncio
async def test_create_data_record(
    db_session: AsyncSession,
    test_owner_id: str,
    test_app_id: str,
    cleanup_test_data,
):
    """测试创建数据记录"""
    # 创建记录
    record_param = CreateAppDataRecordsParam(
        owner_id=test_owner_id,
        app_id=test_app_id,
        installation_id='test_installation_001',
        resource_id='test_resource',
        record_key='user_001',
        data_json={'name': 'Test User', 'age': 25},
    )
    record = await app_data_records_dao.create(db_session, record_param)

    assert record is not None
    assert record.owner_id == test_owner_id
    assert record.app_id == test_app_id
    assert record.resource_id == 'test_resource'
    assert record.record_key == 'user_001'
    assert record.data_json['name'] == 'Test User'
    assert record.data_json['age'] == 25


@pytest.mark.asyncio
async def test_query_data_records(
    db_session: AsyncSession,
    test_owner_id: str,
    test_app_id: str,
    cleanup_test_data,
):
    """测试查询数据记录"""
    # 创建多条记录
    for i in range(5):
        record_param = CreateAppDataRecordsParam(
            owner_id=test_owner_id,
            app_id=test_app_id,
            installation_id='test_installation_002',
            resource_id='test_resource',
            record_key=f'user_{i:03d}',
            data_json={'name': f'User {i}', 'index': i},
        )
        await app_data_records_dao.create(db_session, record_param)

    # 查询记录
    result = await db_session.execute(
        select(AppDataRecords).where(
            AppDataRecords.owner_id == test_owner_id,
            AppDataRecords.app_id == test_app_id,
            AppDataRecords.resource_id == 'test_resource',
        )
    )
    records = result.scalars().all()

    assert len(records) == 5


@pytest.mark.asyncio
async def test_data_isolation(
    db_session: AsyncSession,
    cleanup_test_data,
):
    """测试数据隔离"""
    # 创建两个不同 owner 的记录
    record1_param = CreateAppDataRecordsParam(
        owner_id='owner_001',
        app_id='app_001',
        installation_id='installation_001',
        resource_id='test_resource',
        record_key='shared_key',
        data_json={'owner': 'owner_001'},
    )
    record1 = await app_data_records_dao.create(db_session, record1_param)

    record2_param = CreateAppDataRecordsParam(
        owner_id='owner_002',
        app_id='app_002',
        installation_id='installation_002',
        resource_id='test_resource',
        record_key='shared_key',
        data_json={'owner': 'owner_002'},
    )
    record2 = await app_data_records_dao.create(db_session, record2_param)

    # 验证数据隔离
    assert record1.data_json['owner'] == 'owner_001'
    assert record2.data_json['owner'] == 'owner_002'
    assert record1.id != record2.id
