from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnGroupMembersSchemaBase(SchemaBase):
    """HASN 群成员基础模型"""
    conversation_id: str | UUID = Field(description='群会话 ID（关联 hasn_conversations）')
    member_id: str = Field(description='成员 hasn_id')
    member_type: str = Field(description='成员类型 (human:人类:blue/agent:代理:green)')
    member_star_id: str = Field(description='成员唤星号')
    member_name: str = Field(description='成员名称')
    role: str = Field(description='角色 (owner:群主:red/admin:管理员:orange/member:成员:blue)')
    muted: bool = Field(description='是否免打扰')
    joined_at: datetime | None = Field(None, description='加入时间')
    invited_by: str | None = Field(None, description='邀请者 hasn_id')


class CreateHasnGroupMembersParam(HasnGroupMembersSchemaBase):
    """创建HASN 群成员参数"""


class UpdateHasnGroupMembersParam(HasnGroupMembersSchemaBase):
    """更新HASN 群成员参数"""


class DeleteHasnGroupMembersParam(SchemaBase):
    """删除HASN 群成员参数"""

    pks: list[int] = Field(description='HASN 群成员 ID 列表')


class GetHasnGroupMembersDetail(HasnGroupMembersSchemaBase):
    """HASN 群成员详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
