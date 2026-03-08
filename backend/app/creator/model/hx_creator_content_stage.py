from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText


class HxCreatorContentStage(Base):
    """内容阶段产出表"""

    __tablename__ = 'hx_creator_content_stage'

    id: Mapped[id_key] = mapped_column(init=False)
    content_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联内容ID')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联用户ID')
    stage: Mapped[str] = mapped_column(sa.String(30), default='', comment='阶段：research/outline/first_draft/final_draft/cover/video_script')
    content_text: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='产出内容文本')
    file_url: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='产出文件URL（图片/视频）')
    status: Mapped[str | None] = mapped_column(sa.String(20), default=None, comment='状态：draft/approved/archived')
    version: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='版本号')
    source_type: Mapped[str | None] = mapped_column(sa.String(20), default=None, comment='来源：ai_generated/human_edited/imported')
    meta_data: Mapped[dict | None] = mapped_column('metadata',postgresql.JSONB(), default=None, comment='扩展信息JSON')
