from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.codegen_test.crud.crud_codegen_test_task import codegen_test_task_dao
from backend.app.codegen_test.model import CodegenTestTask
from backend.app.codegen_test.schema.codegen_test_task import CreateCodegenTestTaskParam, DeleteCodegenTestTaskParam, UpdateCodegenTestTaskParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class CodegenTestTaskService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> CodegenTestTask:
        """
        获取测试任务

        :param db: 数据库会话
        :param pk: 测试任务 ID
        :return:
        """
        codegen_test_task = await codegen_test_task_dao.get(db, pk)
        if not codegen_test_task:
            raise errors.NotFoundError(msg='测试任务不存在')
        return codegen_test_task

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取测试任务列表

        :param db: 数据库会话
        :return:
        """
        codegen_test_task_select = await codegen_test_task_dao.get_select()
        return await paging_data(db, codegen_test_task_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[CodegenTestTask]:
        """
        获取所有测试任务

        :param db: 数据库会话
        :return:
        """
        codegen_test_tasks = await codegen_test_task_dao.get_all(db)
        return codegen_test_tasks

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateCodegenTestTaskParam) -> None:
        """
        创建测试任务

        :param db: 数据库会话
        :param obj: 创建测试任务参数
        :return:
        """
        await codegen_test_task_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateCodegenTestTaskParam) -> int:
        """
        更新测试任务

        :param db: 数据库会话
        :param pk: 测试任务 ID
        :param obj: 更新测试任务参数
        :return:
        """
        count = await codegen_test_task_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteCodegenTestTaskParam) -> int:
        """
        删除测试任务

        :param db: 数据库会话
        :param obj: 测试任务 ID 列表
        :return:
        """
        count = await codegen_test_task_dao.delete(db, obj.pks)
        return count


codegen_test_task_service: CodegenTestTaskService = CodegenTestTaskService()
