from datetime import datetime
from typing import Optional
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AutoShareConfig(SchemaBase):
    """自动分享配置"""
    permission: str = Field(default='view', description='分享权限(view只读/edit可编辑)')
    expires_hours: int = Field(default=72, description='过期时间（小时）')
    password: Optional[str] = Field(None, description='分享密码（可选）')


class CreateHuanxingDocumentParam(SchemaBase):
    """创建唤星文档参数"""
    title: str = Field(description='文档标题')
    content: str = Field(description='Markdown内容')
    tags: Optional[list[str]] = Field(None, description='标签列表')
    status: str = Field(default='draft', description='状态(draft/published/archived)')
    auto_share: Optional[AutoShareConfig] = Field(None, description='自动分享配置')


class UpdateHuanxingDocumentParam(SchemaBase):
    """更新唤星文档参数"""
    title: Optional[str] = Field(None, description='文档标题')
    content: Optional[str] = Field(None, description='完整内容（替换模式）')
    append: Optional[str] = Field(None, description='追加内容（与content互斥）')
    tags: Optional[list[str]] = Field(None, description='标签列表')
    status: Optional[str] = Field(None, description='状态')
    save_version: bool = Field(default=False, description='是否保存版本')


class AutosaveParam(SchemaBase):
    """自动保存参数"""
    content: str = Field(description='文档内容')


class ShareSettingsParam(SchemaBase):
    """分享设置参数"""
    permission: str = Field(default='view', description='权限(view/edit)')
    expires_hours: int = Field(default=72, description='过期时间(小时)')
    password: Optional[str] = Field(None, description='密码(可选)')


class HuanxingDocumentSchemaBase(SchemaBase):
    """唤星文档基础模型"""
    uuid: str = Field(description='文档UUID')
    user_id: int = Field(description='用户ID')
    title: str = Field(description='文档标题')
    content: str | None = Field(None, description='Markdown内容')
    summary: str | None = Field(None, description='摘要（自动截取或手动设置）')
    tags: str | None = Field(None, description='标签（JSON数组）')
    word_count: int = Field(description='字数统计')
    status: str = Field(description='状态(draft草稿/published已发布/archived已归档)')
    is_public: bool = Field(description='是否公开')
    created_by: str = Field(description='创建来源(user用户/agent智能体)')
    agent_id: str | None = Field(None, description='Agent ID')
    share_token: str | None = Field(None, description='分享链接token')
    share_password: str | None = Field(None, description='分享密码(bcrypt hash)')
    share_permission: str | None = Field(None, description='分享权限(view只读/edit可编辑)')
    share_expires_at: datetime | None = Field(None, description='分享链接过期时间')
    current_version: int = Field(description='当前版本号')
    created_at: datetime = Field(description='创建时间')
    updated_at: datetime = Field(description='更新时间')
    deleted_at: datetime | None = Field(None, description='删除时间(软删除)')


class DeleteHuanxingDocumentParam(SchemaBase):
    """删除唤星文档参数"""
    pks: list[int] = Field(description='唤星文档 ID 列表')


class GetHuanxingDocumentDetail(HuanxingDocumentSchemaBase):
    """唤星文档详情"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_time: datetime
    updated_time: datetime | None = None
