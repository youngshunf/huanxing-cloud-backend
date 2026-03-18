from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class LlmNewapiUserMapping(Base):
    """唤星用户与 new-api 用户映射表"""

    __tablename__ = 'llm_newapi_user_mapping'

    id: Mapped[id_key] = mapped_column(init=False)
    huanxing_user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='唤星 sys_user.id')
    newapi_user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='new-api users.id')
    newapi_token_key: Mapped[str] = mapped_column(sa.String(48), default='', comment='new-api tokens.key（用户默认 API Key）')
    newapi_token_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='new-api tokens.id')
    app_code: Mapped[str] = mapped_column(sa.String(32), default='', comment='应用标识 (huanxing:唤星/zhixiaoya:知小鸦)')
    status: Mapped[str] = mapped_column(sa.String(16), default='', comment='状态 (active:启用:green/disabled:禁用:red)')
