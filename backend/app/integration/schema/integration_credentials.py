from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class IntegrationCredentialsSchemaBase(SchemaBase):
    """用户第三方应用凭证基础模型"""
    user_id: int = Field(description='用户 ID')
    app_id: str = Field(description='应用唯一标识')
    credentials: dict = Field(description='凭证信息（JSON 格式，如 API Key、Access Token 等）')
    is_active: bool = Field(description='是否激活')
    expires_at: datetime | None = Field(None, description='凭证过期时间')


class CreateIntegrationCredentialsParam(IntegrationCredentialsSchemaBase):
    """创建用户第三方应用凭证参数"""


class UpdateIntegrationCredentialsParam(IntegrationCredentialsSchemaBase):
    """更新用户第三方应用凭证参数"""


class DeleteIntegrationCredentialsParam(SchemaBase):
    """删除用户第三方应用凭证参数"""

    pks: list[int] = Field(description='用户第三方应用凭证 ID 列表')


class GetIntegrationCredentialsDetail(IntegrationCredentialsSchemaBase):
    """用户第三方应用凭证详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
