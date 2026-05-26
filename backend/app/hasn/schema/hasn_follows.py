from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnFollowsSchemaBase(SchemaBase):
    """社区关注基础模型"""
    follower_hasn_id: str = Field(description='None')
    target_type: str = Field(description='human / agent / topic')
    target_hasn_id: str = Field(description='被关注对象的 hasn_id 或 topic 标识')
    created_time: datetime = Field(description='None')


class CreateHasnFollowsParam(HasnFollowsSchemaBase):
    """创建社区关注参数"""


class UpdateHasnFollowsParam(HasnFollowsSchemaBase):
    """更新社区关注参数"""


class DeleteHasnFollowsParam(SchemaBase):
    """删除社区关注参数"""

    pks: list[int] = Field(description='社区关注 ID 列表')


class GetHasnFollowsDetail(HasnFollowsSchemaBase):
    """社区关注详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
