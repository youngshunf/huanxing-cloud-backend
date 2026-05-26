from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnLikesSchemaBase(SchemaBase):
    """社区点赞基础模型"""
    user_hasn_id: str = Field(description='None')
    target_type: str = Field(description='None')
    target_id: str = Field(description='None')
    created_time: datetime = Field(description='None')


class CreateHasnLikesParam(HasnLikesSchemaBase):
    """创建社区点赞参数"""


class UpdateHasnLikesParam(HasnLikesSchemaBase):
    """更新社区点赞参数"""


class DeleteHasnLikesParam(SchemaBase):
    """删除社区点赞参数"""

    pks: list[int] = Field(description='社区点赞 ID 列表')


class GetHasnLikesDetail(HasnLikesSchemaBase):
    """社区点赞详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
