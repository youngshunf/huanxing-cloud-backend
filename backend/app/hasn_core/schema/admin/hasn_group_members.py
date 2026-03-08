"""HASN 群成员管理端 Schema"""
from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnGroupMemberSchemaBase(SchemaBase):
    """群成员基础 Schema"""
    conversation_id: str = Field(description='会话ID')
    member_id: str = Field(description='成员hasn_id')
    member_type: str = Field(description='成员类型(human/agent)')
    member_star_id: str = Field(description='成员唤星号')
    member_name: str = Field(description='成员名称')
    role: str | None = Field(None, description='角色(owner/admin/member)')
    muted: bool | None = Field(None, description='是否静音')
    joined_at: datetime | None = Field(None, description='加入时间')
    invited_by: str | None = Field(None, description='邀请者hasn_id')


class CreateHasnGroupMemberParam(HasnGroupMemberSchemaBase):
    """创建群成员参数"""


class UpdateHasnGroupMemberParam(HasnGroupMemberSchemaBase):
    """更新群成员参数"""


class DeleteHasnGroupMemberParam(SchemaBase):
    """删除群成员参数"""
    pks: list[int] = Field(description='群成员 ID 列表')


class GetHasnGroupMemberDetail(HasnGroupMemberSchemaBase):
    """群成员详情"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
