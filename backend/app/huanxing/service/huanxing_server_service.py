from datetime import datetime
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.huanxing.crud.crud_huanxing_server import huanxing_server_dao
from backend.app.huanxing.crud.crud_huanxing_user import huanxing_user_dao
from backend.app.huanxing.model import HuanxingServer
from backend.app.huanxing.schema.huanxing_server import (
    AgentHeartbeatParam,
    AgentRegisterServerParam,
    AgentRegisterServerResponse,
    CreateHuanxingServerParam,
    DashboardResponse,
    DeleteHuanxingServerParam,
    HeartbeatParam,
    HeartbeatResponse,
    ServerStatsResponse,
    UpdateHuanxingServerParam,
)
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.utils.timezone import timezone


class HuanxingServerService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HuanxingServer:
        """
        获取唤星服务器

        :param db: 数据库会话
        :param pk: 唤星服务器 ID
        :return:
        """
        huanxing_server = await huanxing_server_dao.get(db, pk)
        if not huanxing_server:
            raise errors.NotFoundError(msg='唤星服务器不存在')
        return huanxing_server

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取唤星服务器列表

        :param db: 数据库会话
        :return:
        """
        huanxing_server_select = await huanxing_server_dao.get_select()
        return await paging_data(db, huanxing_server_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HuanxingServer]:
        """
        获取所有唤星服务器

        :param db: 数据库会话
        :return:
        """
        huanxing_servers = await huanxing_server_dao.get_all(db)
        return huanxing_servers

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHuanxingServerParam) -> None:
        """
        创建唤星服务器

        :param db: 数据库会话
        :param obj: 创建唤星服务器参数
        :return:
        """
        await huanxing_server_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHuanxingServerParam) -> int:
        """
        更新唤星服务器

        :param db: 数据库会话
        :param pk: 唤星服务器 ID
        :param obj: 更新唤星服务器参数
        :return:
        """
        count = await huanxing_server_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHuanxingServerParam) -> int:
        """
        删除唤星服务器

        :param db: 数据库会话
        :param obj: 唤星服务器 ID 列表
        :return:
        """
        count = await huanxing_server_dao.delete(db, obj.pks)
        return count

    @staticmethod
    async def agent_register(*, db: AsyncSession, obj: AgentRegisterServerParam, client_ip: str) -> AgentRegisterServerResponse:
        """
        Agent 注册/更新服务器

        :param db: 数据库会话
        :param obj: 注册参数
        :param client_ip: 客户端IP（自动获取）
        :return:
        """
        server = await huanxing_server_dao.get_by_server_id(db, obj.server_id)
        is_new = server is None

        ip_address = obj.ip_address or client_ip
        now = timezone.now()

        if is_new:
            # 创建新服务器
            create_param = CreateHuanxingServerParam(
                server_id=obj.server_id,
                server_name=obj.server_name or obj.server_id,
                ip_address=ip_address,
                port=obj.port,
                region=obj.region,
                provider=obj.provider,
                max_users=obj.max_users,
                status='published',
                gateway_status=obj.gateway_status or 'running',
                last_heartbeat=now,
                config={
                    'user_count': obj.user_count,
                    'active_user_count': obj.active_user_count,
                    'openclaw_version': obj.openclaw_version,
                    'plugin_version': obj.plugin_version,
                    'channels': [ch.model_dump() for ch in obj.channels] if obj.channels else [],
                },
            )
            await huanxing_server_dao.create(db, create_param)
        else:
            # 更新现有服务器
            server.ip_address = ip_address
            if obj.server_name:
                server.server_name = obj.server_name
            if obj.port is not None:
                server.port = obj.port
            if obj.region:
                server.region = obj.region
            if obj.provider:
                server.provider = obj.provider
            if obj.max_users is not None:
                server.max_users = obj.max_users
            server.gateway_status = obj.gateway_status or 'running'
            server.last_heartbeat = now
            server.status = 'published'
            server.config = {
                **(server.config or {}),
                'user_count': obj.user_count,
                'active_user_count': obj.active_user_count,
                'openclaw_version': obj.openclaw_version,
                'plugin_version': obj.plugin_version,
                'channels': [ch.model_dump() for ch in obj.channels] if obj.channels else (server.config or {}).get('channels', []),
            }

        return AgentRegisterServerResponse(
            server_id=obj.server_id,
            is_new=is_new,
            status='ok',
        )

    @staticmethod
    async def heartbeat(*, db: AsyncSession, server_id: str, obj: HeartbeatParam | AgentHeartbeatParam) -> HeartbeatResponse:
        """
        服务器心跳上报

        :param db: 数据库会话
        :param server_id: 服务器唯一标识
        :param obj: 心跳参数
        :return:
        """
        server = await huanxing_server_dao.get_by_server_id(db, server_id)
        if not server:
            raise errors.NotFoundError(msg=f'服务器 {server_id} 不存在')

        # 更新服务器状态
        now = timezone.now()
        server.gateway_status = obj.gateway_status
        server.last_heartbeat = now
        server.config = {
            **(server.config or {}),
            'user_count': obj.user_count,
            'active_user_count': obj.active_user_count,
            'cpu_usage': obj.cpu_usage,
            'memory_usage': obj.memory_usage,
            'disk_usage': obj.disk_usage,
            'openclaw_version': obj.openclaw_version,
            'plugin_version': obj.plugin_version,
        }

        return HeartbeatResponse(
            server_id=server_id,
            received_at=now,
            status='ok',
        )

    @staticmethod
    async def get_server_stats(*, db: AsyncSession, server_id: str) -> ServerStatsResponse:
        """
        获取服务器统计数据

        :param db: 数据库会话
        :param server_id: 服务器唯一标识
        :return:
        """
        server = await huanxing_server_dao.get_by_server_id(db, server_id)
        if not server:
            raise errors.NotFoundError(msg=f'服务器 {server_id} 不存在')

        total_users = await huanxing_user_dao.count_by_server(db, server_id)
        active_users = await huanxing_user_dao.count_active_by_server(db, server_id)
        users_by_template = await huanxing_user_dao.count_by_template(db, server_id)

        return ServerStatsResponse(
            server_id=server_id,
            server_name=server.server_name,
            total_users=total_users,
            active_users=active_users,
            users_by_template=users_by_template,
            gateway_status=server.gateway_status,
            last_heartbeat=server.last_heartbeat,
        )

    @staticmethod
    async def get_dashboard(*, db: AsyncSession, server_id: str | None = None) -> DashboardResponse:
        """
        获取数据看板

        :param db: 数据库会话
        :param server_id: 可选，按服务器筛选
        :return:
        """
        # 用户统计
        if server_id:
            total_users = await huanxing_user_dao.count_by_server(db, server_id)
            active_users = await huanxing_user_dao.count_active_by_server(db, server_id)
        else:
            total_users = await huanxing_user_dao.count_total(db)
            active_users = await huanxing_user_dao.count_total_active(db)

        # 服务器统计
        all_servers = await huanxing_server_dao.get_all(db)
        total_servers = len(all_servers)
        active_servers = sum(1 for s in all_servers if s.status == 1)

        # 按服务器分布
        users_by_server = []
        for s in all_servers:
            count = await huanxing_user_dao.count_by_server(db, s.server_id)
            users_by_server.append({
                'server_id': s.server_id,
                'server_name': s.server_name,
                'user_count': count,
                'gateway_status': s.gateway_status,
            })

        # 按模板分布
        users_by_template = await huanxing_user_dao.count_by_template(db, server_id)

        return DashboardResponse(
            total_users=total_users,
            active_users=active_users,
            total_servers=total_servers,
            active_servers=active_servers,
            users_by_server=users_by_server,
            users_by_template=users_by_template,
        )


huanxing_server_service: HuanxingServerService = HuanxingServerService()
