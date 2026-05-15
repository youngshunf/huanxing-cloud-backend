from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppDevelopersSchemaBase(SchemaBase):
    """应用开发者基础模型"""
    developer_id: str | UUID = Field(description='开发者 ID')
    owner_id: str = Field(description='关联的 Owner ID')
    display_name: str = Field(description='显示名称')
    email: str = Field(description='邮箱')
    company_name: str | None = Field(None, description='None')
    website_url: str | None = Field(None, description='None')
    verification_status: str = Field(description='认证状态 (unverified:未认证:gray/pending:待审核:blue/verified:已认证:green/rejected:已拒绝:red)')
    verified_at: datetime | None = Field(None, description='None')
    status: str = Field(description='状态 (active:活跃:green/suspended:暂停:orange/banned:封禁:red)')
    created_time: datetime = Field(description='None')
    updated_time: datetime = Field(description='None')


class CreateAppDevelopersParam(AppDevelopersSchemaBase):
    """创建应用开发者参数"""


class UpdateAppDevelopersParam(AppDevelopersSchemaBase):
    """更新应用开发者参数"""


class DeleteAppDevelopersParam(SchemaBase):
    """删除应用开发者参数"""

    pks: list[int] = Field(description='应用开发者 ID 列表')


class GetAppDevelopersDetail(AppDevelopersSchemaBase):
    """应用开发者详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
