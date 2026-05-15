from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppReviewsSchemaBase(SchemaBase):
    """App 审核记录基础模型"""
    review_id: str | UUID = Field(description='审核 ID')
    app_id: str = Field(description='None')
    version_id: str | UUID = Field(description='None')
    review_type: str = Field(description='审核类型 (content:内容审核:blue/security:安全审核:red/ui:UI审核:green/frontend:前端审核:purple)')
    reviewer_id: str = Field(description='None')
    review_status: str = Field(description='审核状态 (pending:待审核:blue/approved:已批准:green/rejected:已拒绝:red/changes_requested:需要修改:orange)')
    review_notes: str | None = Field(None, description='None')
    created_time: datetime = Field(description='None')
    updated_time: datetime = Field(description='None')


class CreateAppReviewsParam(AppReviewsSchemaBase):
    """创建App 审核记录参数"""


class UpdateAppReviewsParam(AppReviewsSchemaBase):
    """更新App 审核记录参数"""


class DeleteAppReviewsParam(SchemaBase):
    """删除App 审核记录参数"""

    pks: list[int] = Field(description='App 审核记录 ID 列表')


class GetAppReviewsDetail(AppReviewsSchemaBase):
    """App 审核记录详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
