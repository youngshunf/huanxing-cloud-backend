from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_tenant_sandboxes import hasn_tenant_sandboxes_dao
from backend.app.hasn.model import HasnTenantSandboxes
from backend.app.hasn.schema.hasn_tenant_sandboxes import CreateHasnTenantSandboxesParam, DeleteHasnTenantSandboxesParam, UpdateHasnTenantSandboxesParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnTenantSandboxesService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnTenantSandboxes:
        """
        获取HASN Tenant Sandbox lifecycle 

        :param db: 数据库会话
        :param pk: HASN Tenant Sandbox lifecycle  ID
        :return:
        """
        hasn_tenant_sandboxes = await hasn_tenant_sandboxes_dao.get(db, pk)
        if not hasn_tenant_sandboxes:
            raise errors.NotFoundError(msg='HASN Tenant Sandbox lifecycle 不存在')
        return hasn_tenant_sandboxes

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取HASN Tenant Sandbox lifecycle 列表

        :param db: 数据库会话
        :return:
        """
        hasn_tenant_sandboxes_select = await hasn_tenant_sandboxes_dao.get_select()
        return await paging_data(db, hasn_tenant_sandboxes_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnTenantSandboxes]:
        """
        获取所有HASN Tenant Sandbox lifecycle 

        :param db: 数据库会话
        :return:
        """
        hasn_tenant_sandboxess = await hasn_tenant_sandboxes_dao.get_all(db)
        return hasn_tenant_sandboxess

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnTenantSandboxesParam) -> None:
        """
        创建HASN Tenant Sandbox lifecycle 

        :param db: 数据库会话
        :param obj: 创建HASN Tenant Sandbox lifecycle 参数
        :return:
        """
        await hasn_tenant_sandboxes_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnTenantSandboxesParam) -> int:
        """
        更新HASN Tenant Sandbox lifecycle 

        :param db: 数据库会话
        :param pk: HASN Tenant Sandbox lifecycle  ID
        :param obj: 更新HASN Tenant Sandbox lifecycle 参数
        :return:
        """
        count = await hasn_tenant_sandboxes_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnTenantSandboxesParam) -> int:
        """
        删除HASN Tenant Sandbox lifecycle 

        :param db: 数据库会话
        :param obj: HASN Tenant Sandbox lifecycle  ID 列表
        :return:
        """
        count = await hasn_tenant_sandboxes_dao.delete(db, obj.pks)
        return count


hasn_tenant_sandboxes_service: HasnTenantSandboxesService = HasnTenantSandboxesService()
