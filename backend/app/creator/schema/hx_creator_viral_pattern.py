from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HxCreatorViralPatternSchemaBase(SchemaBase):
    """爆款模式库基础模型"""
    project_id: int | None = Field(None, description='关联项目ID（NULL为全局模式）')
    user_id: int | None = Field(None, description='关联用户ID（NULL为系统级）')
    platform: str | None = Field(None, description='适用平台')
    category: str = Field(description='分类：hook/structure/title/cta/visual/rhythm')
    name: str = Field(description='模式名称')
    description: str | None = Field(None, description='模式描述')
    template: str | None = Field(None, description='模式模板')
    examples: dict | None = Field(None, description='示例JSON数组')
    source: str | None = Field(None, description='来源：manual/ai_extracted/community/system')
    usage_count: int | None = Field(None, description='使用次数')
    success_rate: float | None = Field(None, description='成功率')
    tags: dict | None = Field(None, description='标签JSON数组')


class CreateHxCreatorViralPatternParam(HxCreatorViralPatternSchemaBase):
    """创建爆款模式库参数"""


class UpdateHxCreatorViralPatternParam(HxCreatorViralPatternSchemaBase):
    """更新爆款模式库参数"""


class DeleteHxCreatorViralPatternParam(SchemaBase):
    """删除爆款模式库参数"""

    pks: list[int] = Field(description='爆款模式库 ID 列表')


class GetHxCreatorViralPatternDetail(HxCreatorViralPatternSchemaBase):
    """爆款模式库详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
