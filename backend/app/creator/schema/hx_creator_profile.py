from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HxCreatorProfileSchemaBase(SchemaBase):
    """账号画像基础模型"""
    project_id: int = Field(description='关联项目ID')
    user_id: int = Field(description='关联用户ID')
    niche: str = Field(description='赛道/领域：美食、旅行、科技、教育')
    sub_niche: str | None = Field(None, description='细分赛道：家常菜、烘焙、减脂餐')
    persona: str | None = Field(None, description='人设：美食达人/料理小白/专业厨师')
    target_audience: str | None = Field(None, description='目标受众描述')
    tone: str | None = Field(None, description='内容调性：轻松幽默/专业严谨/温暖治愈')
    keywords: dict | None = Field(None, description='核心关键词JSON数组')
    bio: str | None = Field(None, description='简介文案')
    content_pillars: dict | None = Field(None, description='内容支柱JSON数组')
    posting_frequency: str | None = Field(None, description='发布频率：如每周3-4篇')
    best_posting_time: str | None = Field(None, description='最佳发布时间')
    style_references: dict | None = Field(None, description='风格参考账号JSON数组')
    taboo_topics: dict | None = Field(None, description='避免话题JSON数组')
    pillar_weights: dict | None = Field(None, description='支柱权重JSON（根据数据反馈调整）')
    pillar_weights_updated_at: datetime | None = Field(None, description='支柱权重更新时间')


class CreateHxCreatorProfileParam(HxCreatorProfileSchemaBase):
    """创建账号画像参数"""


class UpdateHxCreatorProfileParam(HxCreatorProfileSchemaBase):
    """更新账号画像参数"""


class DeleteHxCreatorProfileParam(SchemaBase):
    """删除账号画像参数"""

    pks: list[int] = Field(description='账号画像 ID 列表')


class GetHxCreatorProfileDetail(HxCreatorProfileSchemaBase):
    """账号画像详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
