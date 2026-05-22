from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnCollectionsSchemaBase(SchemaBase):
    """社区收藏夹基础模型"""
    collection_id: str = Field(description='None')
    owner_hasn_id: str = Field(description='None')
    name: str = Field(description='None')
    is_public: bool = Field(description='None')
    item_count: int = Field(description='None')
    create_time: datetime = Field(description='None')
    update_time: datetime | None = Field(None, description='None')


class CreateHasnCollectionsParam(HasnCollectionsSchemaBase):
    """创建社区收藏夹参数"""


class UpdateHasnCollectionsParam(HasnCollectionsSchemaBase):
    """更新社区收藏夹参数"""


class DeleteHasnCollectionsParam(SchemaBase):
    """删除社区收藏夹参数"""

    pks: list[int] = Field(description='社区收藏夹 ID 列表')


class GetHasnCollectionsDetail(HasnCollectionsSchemaBase):
    """社区收藏夹详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
