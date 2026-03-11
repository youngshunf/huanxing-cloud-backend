from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.codegen_test.model import CodegenTestTask
from backend.app.codegen_test.schema.codegen_test_task import CreateCodegenTestTaskParam, UpdateCodegenTestTaskParam


class CRUDCodegenTestTask(CRUDPlus[CodegenTestTask]):
    async def get(self, db: AsyncSession, pk: int) -> CodegenTestTask | None:
        """
        获取测试任务

        :param db: 数据库会话
        :param pk: 测试任务 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取测试任务列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[CodegenTestTask]:
        """
        获取所有测试任务

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateCodegenTestTaskParam) -> None:
        """
        创建测试任务

        :param db: 数据库会话
        :param obj: 创建测试任务参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateCodegenTestTaskParam) -> int:
        """
        更新测试任务

        :param db: 数据库会话
        :param pk: 测试任务 ID
        :param obj: 更新 测试任务参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除测试任务

        :param db: 数据库会话
        :param pks: 测试任务 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


codegen_test_task_dao: CRUDCodegenTestTask = CRUDCodegenTestTask(CodegenTestTask)
