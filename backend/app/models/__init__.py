"""M1 移动端跨模块共用 ORM 模型 (infra 层, 与 hasn/ 业务表分离).

PRD: scripts/ralph-B/prd.json 中 B3+ 均落在 backend/app/models/。
"""
from backend.app.models.push_token import PushChannel as PushChannel
from backend.app.models.push_token import PushToken as PushToken
from backend.app.models.push_token_audit import PushTokenAudit as PushTokenAudit
