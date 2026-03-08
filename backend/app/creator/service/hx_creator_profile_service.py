from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.creator.crud.crud_hx_creator_profile import hx_creator_profile_dao
from backend.app.creator.model import HxCreatorProfile
from backend.app.creator.schema.hx_creator_profile import CreateHxCreatorProfileParam, DeleteHxCreatorProfileParam, UpdateHxCreatorProfileParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HxCreatorProfileService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HxCreatorProfile:
        """
        获取账号画像

        :param db: 数据库会话
        :param pk: 账号画像 ID
        :return:
        """
        hx_creator_profile = await hx_creator_profile_dao.get(db, pk)
        if not hx_creator_profile:
            raise errors.NotFoundError(msg='账号画像不存在')
        return hx_creator_profile

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取账号画像列表

        :param db: 数据库会话
        :return:
        """
        hx_creator_profile_select = await hx_creator_profile_dao.get_select()
        return await paging_data(db, hx_creator_profile_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HxCreatorProfile]:
        """
        获取所有账号画像

        :param db: 数据库会话
        :return:
        """
        hx_creator_profiles = await hx_creator_profile_dao.get_all(db)
        return hx_creator_profiles

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHxCreatorProfileParam) -> None:
        """
        创建账号画像

        :param db: 数据库会话
        :param obj: 创建账号画像参数
        :return:
        """
        await hx_creator_profile_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHxCreatorProfileParam) -> int:
        """
        更新账号画像

        :param db: 数据库会话
        :param pk: 账号画像 ID
        :param obj: 更新账号画像参数
        :return:
        """
        count = await hx_creator_profile_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHxCreatorProfileParam) -> int:
        """
        删除账号画像

        :param db: 数据库会话
        :param obj: 账号画像 ID 列表
        :return:
        """
        count = await hx_creator_profile_dao.delete(db, obj.pks)
        return count


hx_creator_profile_service: HxCreatorProfileService = HxCreatorProfileService()
