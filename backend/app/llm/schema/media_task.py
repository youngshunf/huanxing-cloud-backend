"""媒体任务管理 Schema（管理后台用）"""

from datetime import datetime
from decimal import Decimal

from backend.common.schema import SchemaBase


class MediaTaskResult(SchemaBase):
    """媒体任务列表/详情响应"""

    id: int
    task_id: str
    user_id: int
    api_key_id: int
    model_name: str
    provider_id: int
    media_type: str
    prompt: str
    status: str
    progress: int
    params: dict | None = None
    vendor_task_id: str | None = None
    vendor_urls: list | None = None
    oss_urls: list | None = None
    error_code: str | None = None
    error_message: str | None = None
    webhook_url: str | None = None
    credits_cost: Decimal
    credits_pre_deducted: Decimal
    poll_count: int
    ip_address: str | None = None
    completed_at: datetime | None = None
    created_time: datetime
    updated_time: datetime | None = None


class MediaTaskListParams(SchemaBase):
    """媒体任务列表查询参数"""

    user_id: int | None = None
    media_type: str | None = None
    status: str | None = None
    model_name: str | None = None
