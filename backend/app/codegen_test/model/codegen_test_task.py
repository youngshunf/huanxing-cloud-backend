from datetime import datetime, date
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText


class CodegenTestTask(Base):
    """测试任务表"""

    __tablename__ = 'codegen_test_task'

    id: Mapped[id_key] = mapped_column(init=False)
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='用户ID')
    title: Mapped[str] = mapped_column(sa.String(200), default='', comment='任务标题')
    description: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='任务描述')
    status: Mapped[int | None] = mapped_column(sa.SMALLINT(), default=None, comment='状态 (0:待办:blue/1:进行中:orange/2:已完成:green/3:已取消:red)')
    priority: Mapped[int | None] = mapped_column(sa.SMALLINT(), default=None, comment='优先级 (1:低:blue/2:中:orange/3:高:red)')
    category: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='分类 (work:工作:blue/study:学习:green/life:生活:purple)')
    type: Mapped[str | None] = mapped_column(sa.String(32), default=None, comment='类型 (normal:普通:blue/urgent:紧急:red/scheduled:计划:green)')
    progress: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='进度百分比(0-100)')
    due_date: Mapped[date | None] = mapped_column(sa.DATE(), default=None, comment='截止日期')
    remark: Mapped[str | None] = mapped_column(sa.String(512), default=None, comment='备注')
