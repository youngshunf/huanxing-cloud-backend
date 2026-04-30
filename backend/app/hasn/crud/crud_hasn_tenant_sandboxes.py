from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn.model import HasnTenantSandboxes
from backend.app.hasn.schema.hasn_tenant_sandboxes import CreateHasnTenantSandboxesParam, UpdateHasnTenantSandboxesParam


class CRUDHasnTenantSandboxes(CRUDPlus[HasnTenantSandboxes]):
    async def get(self, db: AsyncSession, pk: int) -> HasnTenantSandboxes | None:
        """
        获取HASN Tenant Sandbox lifecycle 

        :param db: 数据库会话
        :param pk: HASN Tenant Sandbox lifecycle  ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取HASN Tenant Sandbox lifecycle 列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnTenantSandboxes]:
        """
        获取所有HASN Tenant Sandbox lifecycle 

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHasnTenantSandboxesParam) -> None:
        """
        创建HASN Tenant Sandbox lifecycle 

        :param db: 数据库会话
        :param obj: 创建HASN Tenant Sandbox lifecycle 参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHasnTenantSandboxesParam) -> int:
        """
        更新HASN Tenant Sandbox lifecycle 

        :param db: 数据库会话
        :param pk: HASN Tenant Sandbox lifecycle  ID
        :param obj: 更新 HASN Tenant Sandbox lifecycle 参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除HASN Tenant Sandbox lifecycle 

        :param db: 数据库会话
        :param pks: HASN Tenant Sandbox lifecycle  ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hasn_tenant_sandboxes_dao: CRUDHasnTenantSandboxes = CRUDHasnTenantSandboxes(HasnTenantSandboxes)
