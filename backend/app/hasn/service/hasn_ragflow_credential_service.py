from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_ragflow_credential import hasn_ragflow_credential_dao
from backend.app.hasn.model import HasnRagflowCredential
from backend.app.hasn.schema.hasn_ragflow_credential import (
    CreateHasnRagflowCredentialParam,
    DeleteHasnRagflowCredentialParam,
    UpdateHasnRagflowCredentialParam,
)
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnRagflowCredentialService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnRagflowCredential:
        item = await hasn_ragflow_credential_dao.get(db, pk)
        if not item:
            raise errors.NotFoundError(msg='RAGFlow 凭据不存在')
        return item

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        return await paging_data(db, await hasn_ragflow_credential_dao.get_select())

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnRagflowCredential]:
        return await hasn_ragflow_credential_dao.get_all(db)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnRagflowCredentialParam) -> None:
        await hasn_ragflow_credential_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnRagflowCredentialParam) -> int:
        return await hasn_ragflow_credential_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnRagflowCredentialParam) -> int:
        return await hasn_ragflow_credential_dao.delete(db, obj.pks)


hasn_ragflow_credential_service: HasnRagflowCredentialService = HasnRagflowCredentialService()
