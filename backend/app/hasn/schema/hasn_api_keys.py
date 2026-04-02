from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class CreateApiKeyReq(BaseModel):
    name: str = Field(description='API Key 名称 (如: 办公室 Mac)')

class ApiKeyOut(BaseModel):
    client_id: str = Field(description='节点 ID')
    device_name: str | None = Field(None, description='API Key 名称')
    created_time: datetime | None = Field(None, description='创建时间')
    last_seen_at: datetime | None = Field(None, description='最后使用时间')

class CreateApiKeyRes(ApiKeyOut):
    api_key: str = Field(description='明文 API Key (仅返回一次)')
