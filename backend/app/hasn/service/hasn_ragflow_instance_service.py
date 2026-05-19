from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_ragflow_instance import hasn_ragflow_instance_dao
from backend.app.hasn.model import HasnRagflowInstance
from backend.app.hasn.schema.hasn_ragflow_instance import (
    CreateHasnRagflowInstanceParam,
    DeleteHasnRagflowInstanceParam,
    UpdateHasnRagflowInstanceParam,
)
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnRagflowInstanceService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnRagflowInstance:
        item = await hasn_ragflow_instance_dao.get(db, pk)
        if not item:
            raise errors.NotFoundError(msg='RAGFlow 实例不存在')
        return item

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        return await paging_data(db, await hasn_ragflow_instance_dao.get_select())

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnRagflowInstance]:
        return await hasn_ragflow_instance_dao.get_all(db)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnRagflowInstanceParam) -> None:
        await hasn_ragflow_instance_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnRagflowInstanceParam) -> int:
        return await hasn_ragflow_instance_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnRagflowInstanceParam) -> int:
        return await hasn_ragflow_instance_dao.delete(db, obj.pks)


hasn_ragflow_instance_service: HasnRagflowInstanceService = HasnRagflowInstanceService()
