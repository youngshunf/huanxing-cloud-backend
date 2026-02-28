from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.huanxing.crud.crud_huanxing_user import huanxing_user_dao
from backend.app.huanxing.model import HuanxingUser
from backend.app.huanxing.schema.huanxing_user import CreateHuanxingUserParam, DeleteHuanxingUserParam, UpdateHuanxingUserParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HuanxingUserService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HuanxingUser:
        """
        获取唤星用户

        :param db: 数据库会话
        :param pk: 唤星用户 ID
        :return:
        """
        huanxing_user = await huanxing_user_dao.get(db, pk)
        if not huanxing_user:
            raise errors.NotFoundError(msg='唤星用户不存在')
        return huanxing_user

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取唤星用户列表

        :param db: 数据库会话
        :return:
        """
        huanxing_user_select = await huanxing_user_dao.get_select()
        return await paging_data(db, huanxing_user_select)

    @staticmethod
    async def get_list_by_server(*, db: AsyncSession, server_id: str) -> dict[str, Any]:
        """
        获取指定服务器的唤星用户列表

        :param db: 数据库会话
        :param server_id: 服务器唯一标识
        :return:
        """
        huanxing_user_select = await huanxing_user_dao.get_select_by_server(server_id)
        return await paging_data(db, huanxing_user_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HuanxingUser]:
        """
        获取所有唤星用户

        :param db: 数据库会话
        :return:
        """
        huanxing_users = await huanxing_user_dao.get_all(db)
        return huanxing_users

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHuanxingUserParam) -> None:
        """
        创建唤星用户

        :param db: 数据库会话
        :param obj: 创建唤星用户参数
        :return:
        """
        await huanxing_user_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHuanxingUserParam) -> int:
        """
        更新唤星用户

        :param db: 数据库会话
        :param pk: 唤星用户 ID
        :param obj: 更新唤星用户参数
        :return:
        """
        count = await huanxing_user_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHuanxingUserParam) -> int:
        """
        删除唤星用户

        :param db: 数据库会话
        :param obj: 唤星用户 ID 列表
        :return:
        """
        count = await huanxing_user_dao.delete(db, obj.pks)
        return count


huanxing_user_service: HuanxingUserService = HuanxingUserService()
