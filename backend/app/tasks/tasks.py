"""Celery 自动发现入口.

`backend.app.task.celery:find_task_packages` 扫描 `backend/app/` 下含 `tasks.py`
的目录, `autodiscover_tasks` 再 `from <pkg> import tasks`. 本文件是该入口,
只需导入同目录下的任务模块即可让装饰器注册到 celery_app.
"""
from backend.app.tasks.push_message import push_message  # noqa: F401
