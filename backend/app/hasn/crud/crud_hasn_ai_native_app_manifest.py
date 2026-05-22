from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn.model import HasnAiNativeAppManifest
from backend.app.hasn.schema.ai_native_app import CreateAiNativeAppManifestParam, UpdateAiNativeAppManifestParam


class CRUDHasnAiNativeAppManifest(CRUDPlus[HasnAiNativeAppManifest]):
    async def get(self, db: AsyncSession, pk: int) -> HasnAiNativeAppManifest | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnAiNativeAppManifest]:
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateAiNativeAppManifestParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAiNativeAppManifestParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)

    async def get_by_app_version(self, db: AsyncSession, *, app_id: str, version: str) -> HasnAiNativeAppManifest | None:
        return await self.select_model_by_column(db, app_id=app_id, version=version)

    async def get_latest_by_app_id(
        self, db: AsyncSession, *, app_id: str, status: str | None = None
    ) -> HasnAiNativeAppManifest | None:
        stmt = await self.select_order('id', 'desc')
        stmt = stmt.where(HasnAiNativeAppManifest.app_id == app_id)
        if status:
            stmt = stmt.where(HasnAiNativeAppManifest.status == status)
        return (await db.execute(stmt)).scalars().first()


hasn_ai_native_app_manifest_dao: CRUDHasnAiNativeAppManifest = CRUDHasnAiNativeAppManifest(HasnAiNativeAppManifest)
