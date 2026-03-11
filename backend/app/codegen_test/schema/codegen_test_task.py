from datetime import datetime, date
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class CodegenTestTaskSchemaBase(SchemaBase):
    """测试任务基础模型"""
    user_id: int = Field(description='用户ID')
    title: str = Field(description='任务标题')
    description: str | None = Field(None, description='任务描述')
    status: int | None = Field(None, description='状态 (0:待办:blue/1:进行中:orange/2:已完成:green/3:已取消:red)')
    priority: int | None = Field(None, description='优先级 (1:低:blue/2:中:orange/3:高:red)')
    category: str | None = Field(None, description='分类 (work:工作:blue/study:学习:green/life:生活:purple)')
    type: str | None = Field(None, description='类型 (normal:普通:blue/urgent:紧急:red/scheduled:计划:green)')
    progress: int | None = Field(None, description='进度百分比(0-100)')
    due_date: date | None = Field(None, description='截止日期')
    remark: str | None = Field(None, description='备注')


class CreateCodegenTestTaskParam(CodegenTestTaskSchemaBase):
    """创建测试任务参数"""


class UpdateCodegenTestTaskParam(CodegenTestTaskSchemaBase):
    """更新测试任务参数"""


class DeleteCodegenTestTaskParam(SchemaBase):
    """删除测试任务参数"""

    pks: list[int] = Field(description='测试任务 ID 列表')


class GetCodegenTestTaskDetail(CodegenTestTaskSchemaBase):
    """测试任务详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
