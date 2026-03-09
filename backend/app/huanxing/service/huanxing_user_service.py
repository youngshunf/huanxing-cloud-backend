from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.huanxing.crud.crud_huanxing_user import huanxing_user_dao
from backend.app.huanxing.model import HuanxingUser
from backend.app.huanxing.schema.huanxing_user import (
    CreateHuanxingUserParam,
    DeleteHuanxingUserParam,
    UpdateHuanxingUserParam,
    AgentSyncUserParam,
    AgentUpdateUserParam,
)
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

    @staticmethod
    async def agent_sync(*, db: AsyncSession, obj: AgentSyncUserParam) -> HuanxingUser:
        """
        Agent 同步用户（注册时调用）

        如果 agent_id 已存在则更新，否则创建新记录。

        :param db: 数据库会话
        :param obj: Agent 同步参数
        :return: 创建或更新后的用户记录
        """
        # 先按 agent_id 查找是否已存在
        existing = await huanxing_user_dao.get_by_agent_id(db, obj.agent_id)
        if existing:
            # 更新现有记录
            update_data = UpdateHuanxingUserParam(
                user_id=obj.user_id,
                server_id=obj.server_id,
                agent_id=obj.agent_id,
                star_name=obj.star_name or existing.star_name,
                template=obj.template or existing.template,
                workspace_path=obj.workspace_path or existing.workspace_path,
                channel_type=obj.channel_type or existing.channel_type,
                channel_peer_id=obj.channel_peer_id or existing.channel_peer_id,
                agent_status=1,
            )
            await huanxing_user_dao.update(db, existing.id, update_data)
            await db.refresh(existing)
            return existing
        else:
            # 创建新记录
            create_data = CreateHuanxingUserParam(
                user_id=obj.user_id,
                server_id=obj.server_id,
                agent_id=obj.agent_id,
                star_name=obj.star_name,
                template=obj.template or 'assistant',
                workspace_path=obj.workspace_path,
                channel_type=obj.channel_type,
                channel_peer_id=obj.channel_peer_id,
                agent_status=1,
            )
            await huanxing_user_dao.create(db, create_data)
            await db.flush()
            # 查询刚创建的记录返回
            created = await huanxing_user_dao.get_by_agent_id(db, obj.agent_id)
            if not created:
                raise errors.NotFoundError(msg='用户创建异常，请重试')
            return created

    @staticmethod
    async def agent_update(*, db: AsyncSession, user_id: int, obj: AgentUpdateUserParam) -> int:
        """
        Agent 更新用户信息

        :param db: 数据库会话
        :param user_id: 平台 user_id（sys_user.id）
        :param obj: Agent 更新参数
        :return: 更新行数
        """
        existing = await huanxing_user_dao.get_by_user_id(db, user_id)
        if not existing:
            raise errors.NotFoundError(msg='唤星用户不存在')

        # 只更新传入的非 None 字段
        update_dict = {}
        if obj.agent_id is not None:
            update_dict['agent_id'] = obj.agent_id
        if obj.star_name is not None:
            update_dict['star_name'] = obj.star_name
        if obj.template is not None:
            update_dict['template'] = obj.template
        if obj.workspace_path is not None:
            update_dict['workspace_path'] = obj.workspace_path
        if obj.agent_status is not None:
            update_dict['agent_status'] = obj.agent_status

        if not update_dict:
            return 0

        update_data = UpdateHuanxingUserParam(
            user_id=existing.user_id,
            server_id=existing.server_id,
            **{k: update_dict.get(k, getattr(existing, k)) for k in [
                'agent_id', 'star_name', 'template', 'workspace_path',
                'agent_status', 'channel_type', 'channel_peer_id',
            ]},
        )
        return await huanxing_user_dao.update(db, existing.id, update_data)


huanxing_user_service: HuanxingUserService = HuanxingUserService()
