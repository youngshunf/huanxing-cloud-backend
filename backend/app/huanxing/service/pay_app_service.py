from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.huanxing.crud.crud_pay_app import pay_app_dao
from backend.app.huanxing.model.pay_app import PayApp
from backend.app.huanxing.schema.pay_app import CreatePayAppParam, DeletePayAppParam, UpdatePayAppParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class PayAppService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> PayApp:
        pay_app = await pay_app_dao.get(db, pk)
        if not pay_app:
            raise errors.NotFoundError(msg='支付应用不存在')
        return pay_app

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        select_stmt = await pay_app_dao.get_select()
        return await paging_data(db, select_stmt)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreatePayAppParam) -> None:
        existing = await pay_app_dao.get_by_app_key(db, obj.app_key)
        if existing:
            raise errors.ForbiddenError(msg=f'应用标识 {obj.app_key} 已存在')
        await pay_app_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdatePayAppParam) -> int:
        return await pay_app_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeletePayAppParam) -> int:
        return await pay_app_dao.delete(db, obj.pks)


pay_app_service: PayAppService = PayAppService()
