from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnContactRequestsSchemaBase(SchemaBase):
    """HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）基础模型"""

    from_id: str = Field(description='发起方 hasn_id（恒 human）')
    from_type: str = Field(description='发起方类型 (human:人类:blue/agent:代理:green)')
    to_id: str = Field(description='目标 hasn_id（解析后恒 human）')
    to_type: str = Field(description='目标类型 (human:人类:blue/agent:代理:green)')
    to_owner_id: str = Field(description='审批人 hasn_id（=目标本人，agent 目标则解析为其主人）')
    relation_type: str = Field(
        description='关系类型 (social:社交:blue/commerce:商业:orange/service:履约:green/professional:专业:purple/platform:平台:cyan)'
    )
    requested_trust_level: int = Field(description='请求授予的信任等级（通过时落到 hasn_contacts.trust_level）')
    message: str | None = Field(None, description='请求附言')
    status: str = Field(
        description='状态 (pending:待处理:blue/accepted:已通过:green/rejected:已拒绝:red/withdrawn:已撤回:gray/expired:已过期:gray)'
    )
    decided_by: str | None = Field(None, description='回应人 hasn_id')
    decided_at: datetime | None = Field(None, description='回应时间')
    resulting_contact_id: int | None = Field(None, description='通过后建立的 hasn_contacts 行 ID（审计链）')
    channel_source: str | None = Field(
        None,
        description='来源渠道类型 (wechat:微信:green/feishu:飞书:blue/qq:QQ:cyan/webhook:Webhook:purple/manual:好友请求:gray/system:系统:orange)',
    )


class CreateHasnContactRequestsParam(HasnContactRequestsSchemaBase):
    """创建HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）参数"""


class UpdateHasnContactRequestsParam(HasnContactRequestsSchemaBase):
    """更新HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）参数"""


class DeleteHasnContactRequestsParam(SchemaBase):
    """删除HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）参数"""

    pks: list[int] = Field(description='HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表） ID 列表')


class GetHasnContactRequestsDetail(HasnContactRequestsSchemaBase):
    """HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
