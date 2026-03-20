"""唤星用户 ↔ new-api 用户映射 CRUD + new-api 表直接操作"""

import secrets
import time
from typing import Sequence

from sqlalchemy import Select, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.llm.model import LlmNewapiUserMapping
from backend.app.llm.schema.llm_newapi_user_mapping import CreateLlmNewapiUserMappingParam, UpdateLlmNewapiUserMappingParam


class CRUDLlmNewapiUserMapping(CRUDPlus[LlmNewapiUserMapping]):
    async def get(self, db: AsyncSession, pk: int) -> LlmNewapiUserMapping | None:
        return await self.select_model(db, pk)

    async def get_by_user(
        self, db: AsyncSession, huanxing_user_id: int, app_code: str = 'huanxing'
    ) -> LlmNewapiUserMapping | None:
        """根据唤星用户 ID + app_code 查询映射"""
        stmt = select(LlmNewapiUserMapping).where(
            LlmNewapiUserMapping.huanxing_user_id == huanxing_user_id,
            LlmNewapiUserMapping.app_code == app_code,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[LlmNewapiUserMapping]:
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateLlmNewapiUserMappingParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateLlmNewapiUserMappingParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


class CRUDNewApiDirect:
    """直接操作 new-api 表（raw SQL，避免 GORM schema 差异）"""

    @staticmethod
    def generate_token_key() -> str:
        """生成 new-api 格式的 API Key（数据库存储值，不含 sk- 前缀）

        格式: hx{46 random chars} = 48 chars
        用户使用时加 sk- 前缀: sk-hx{46 random chars}
        new-api 中间件会去掉 sk- 后按 - split 取 parts[0]，
        所以数据库里的 key 不能包含 -
        """
        random_part = secrets.token_urlsafe(48)
        # 只保留字母数字，去掉 - 和 _
        random_part = ''.join(c for c in random_part if c.isalnum())[:46]
        return f'hx{random_part}'

    @staticmethod
    async def create_newapi_user(
        db: AsyncSession,
        *,
        username: str,
        display_name: str,
        quota: int = 50000,
        group: str = 'default',
    ) -> int:
        """在 new-api users 表创建用户，返回 user_id"""
        result = await db.execute(
            text("""
                INSERT INTO users (username, password, display_name, role, status, quota, used_quota,
                                   request_count, "group", aff_code, aff_count, aff_quota, aff_history)
                VALUES (:username, :password, :display_name, 1, 1, :quota, 0, 0, :group, :aff_code, 0, 0, 0)
                RETURNING id
            """),
            {
                'username': username,
                'password': secrets.token_hex(32),
                'display_name': display_name,
                'quota': quota,
                'group': group,
                'aff_code': secrets.token_urlsafe(8),
            },
        )
        row = result.fetchone()
        return row[0]

    @staticmethod
    async def create_newapi_token(
        db: AsyncSession,
        *,
        user_id: int,
        token_key: str,
        name: str = '默认 Key',
        quota: int = 0,
        unlimited_quota: bool = True,
    ) -> int:
        """在 new-api tokens 表创建 token，返回 token_id

        唤星创建的 token 默认无限额度（unlimited_quota=true），
        由 users.quota 统一控制用户可用额度。
        """
        now = int(time.time())
        result = await db.execute(
            text("""
                INSERT INTO tokens (user_id, "key", status, name, created_time, accessed_time,
                                    expired_time, remain_quota, used_quota, unlimited_quota,
                                    model_limits_enabled)
                VALUES (:user_id, :key, 1, :name, :created_time, 0, -1, :quota, 0, :unlimited_quota, false)
                RETURNING id
            """),
            {
                'user_id': user_id,
                'key': token_key,
                'name': name,
                'created_time': now,
                'quota': quota,
                'unlimited_quota': unlimited_quota,
            },
        )
        row = result.fetchone()
        return row[0]

    @staticmethod
    async def update_newapi_quota(
        db: AsyncSession,
        *,
        newapi_user_id: int,
        new_quota: int,
    ) -> None:
        """更新 new-api 的 users.quota（token 为无限额度，无需同步）"""
        await db.execute(
            text('UPDATE users SET quota = :quota WHERE id = :user_id'),
            {'quota': new_quota, 'user_id': newapi_user_id},
        )

    @staticmethod
    async def get_newapi_user_quota(db: AsyncSession, newapi_user_id: int) -> dict | None:
        """查询 new-api 用户的 quota 信息"""
        result = await db.execute(
            text('SELECT id, quota, used_quota, request_count FROM users WHERE id = :user_id'),
            {'user_id': newapi_user_id},
        )
        row = result.fetchone()
        if not row:
            return None
        return {'id': row[0], 'quota': row[1], 'used_quota': row[2], 'request_count': row[3]}

    @staticmethod
    async def get_token_remain_quota(db: AsyncSession, token_id: int) -> int | None:
        """查询 token 剩余 quota"""
        result = await db.execute(
            text('SELECT remain_quota FROM tokens WHERE id = :token_id'),
            {'token_id': token_id},
        )
        row = result.fetchone()
        return row[0] if row else None

    @staticmethod
    async def get_usage_summary(
        db: AsyncSession,
        newapi_user_id: int,
        start_time: int,
        end_time: int,
    ) -> list[dict]:
        """按模型分组查询用量统计"""
        result = await db.execute(
            text("""
                SELECT model_name,
                       SUM(prompt_tokens) AS total_prompt_tokens,
                       SUM(completion_tokens) AS total_completion_tokens,
                       SUM(quota) AS total_quota,
                       COUNT(*) AS request_count
                FROM logs
                WHERE user_id = :user_id
                  AND created_at >= :start_time
                  AND created_at < :end_time
                  AND type = 2
                GROUP BY model_name
                ORDER BY total_quota DESC
            """),
            {'user_id': newapi_user_id, 'start_time': start_time, 'end_time': end_time},
        )
        return [
            {
                'model_name': row[0],
                'prompt_tokens': row[1],
                'completion_tokens': row[2],
                'quota': row[3],
                'request_count': row[4],
            }
            for row in result.fetchall()
        ]

    @staticmethod
    async def get_usage_detail(
        db: AsyncSession,
        newapi_user_id: int,
        start_time: int,
        end_time: int,
        *,
        model_name: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        """查询用量明细（分页），返回 (records, total)"""
        where_clause = 'WHERE user_id = :user_id AND created_at >= :start_time AND created_at < :end_time AND type = 2'
        params: dict = {'user_id': newapi_user_id, 'start_time': start_time, 'end_time': end_time}
        if model_name:
            where_clause += ' AND model_name = :model_name'
            params['model_name'] = model_name

        count_result = await db.execute(text(f'SELECT COUNT(*) FROM logs {where_clause}'), params)
        total = count_result.scalar() or 0

        params['limit'] = limit
        params['offset'] = offset
        result = await db.execute(
            text(f"""
                SELECT id, created_at, model_name, prompt_tokens, completion_tokens,
                       quota, use_time, is_stream, request_id, token_name
                FROM logs {where_clause}
                ORDER BY id DESC LIMIT :limit OFFSET :offset
            """),
            params,
        )
        records = [
            {
                'id': row[0], 'created_at': row[1], 'model_name': row[2],
                'prompt_tokens': row[3], 'completion_tokens': row[4], 'quota': row[5],
                'use_time': row[6], 'is_stream': row[7], 'request_id': row[8], 'token_name': row[9],
            }
            for row in result.fetchall()
        ]
        return records, total


llm_newapi_user_mapping_dao: CRUDLlmNewapiUserMapping = CRUDLlmNewapiUserMapping(LlmNewapiUserMapping)
newapi_direct_dao: CRUDNewApiDirect = CRUDNewApiDirect()
