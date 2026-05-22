from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnCollectionItemsSchemaBase(SchemaBase):
    """社区收藏项基础模型"""
    collection_id: str = Field(description='None')
    target_type: str = Field(description='None')
    target_id: str = Field(description='None')
    create_time: datetime = Field(description='None')


class CreateHasnCollectionItemsParam(HasnCollectionItemsSchemaBase):
    """创建社区收藏项参数"""


class UpdateHasnCollectionItemsParam(HasnCollectionItemsSchemaBase):
    """更新社区收藏项参数"""


class DeleteHasnCollectionItemsParam(SchemaBase):
    """删除社区收藏项参数"""

    pks: list[int] = Field(description='社区收藏项 ID 列表')


class GetHasnCollectionItemsDetail(HasnCollectionItemsSchemaBase):
    """社区收藏项详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
