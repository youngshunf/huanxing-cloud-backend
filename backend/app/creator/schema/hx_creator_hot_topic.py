from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HxCreatorHotTopicSchemaBase(SchemaBase):
    """热榜快照基础模型"""
    platform_id: str = Field(description='平台标识')
    platform_name: str = Field(description='平台名称')
    title: str = Field(description='热点标题')
    url: str | None = Field(None, description='热点链接')
    rank: int | None = Field(None, description='排名')
    heat_score: float | None = Field(None, description='热度分数')
    fetch_source: str = Field(description='数据来源')
    fetched_at: datetime = Field(description='抓取时间')
    batch_date: str = Field(description='批次日期')


class CreateHxCreatorHotTopicParam(HxCreatorHotTopicSchemaBase):
    """创建热榜快照参数"""


class UpdateHxCreatorHotTopicParam(HxCreatorHotTopicSchemaBase):
    """更新热榜快照参数"""


class DeleteHxCreatorHotTopicParam(SchemaBase):
    """删除热榜快照参数"""

    pks: list[int] = Field(description='热榜快照 ID 列表')


class GetHxCreatorHotTopicDetail(HxCreatorHotTopicSchemaBase):
    """热榜快照详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
