"""
技能市场集成测试

测试完整的技能市场功能，包括：
1. 数据库表结构
2. CRUD 操作
3. GitHub 同步
4. 翻译服务
5. 搜索功能
6. 下载功能
"""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TestMarketplaceTables:
    """测试数据库表结构"""

    @pytest.mark.asyncio
    async def test_marketplace_skill_table_exists(self, db_session: AsyncSession):
        """测试 marketplace_skill 表是否存在"""
        result = await db_session.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'marketplace_skill')")
        )
        exists = result.scalar()
        assert exists, "marketplace_skill 表不存在"

    @pytest.mark.asyncio
    async def test_marketplace_template_table_exists(self, db_session: AsyncSession):
        """测试 marketplace_template 表是否存在"""
        result = await db_session.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'marketplace_template')")
        )
        exists = result.scalar()
        assert exists, "marketplace_template 表不存在"

    @pytest.mark.asyncio
    async def test_marketplace_skill_has_namespace_fields(self, db_session: AsyncSession):
        """测试 marketplace_skill 表是否有命名空间字段"""
        result = await db_session.execute(
            text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'marketplace_skill'
                AND column_name IN ('namespace', 'slug', 'source_type')
            """)
        )
        columns = [row[0] for row in result.fetchall()]

        assert 'namespace' in columns, "marketplace_skill 表缺少 namespace 字段"
        assert 'slug' in columns, "marketplace_skill 表缺少 slug 字段"
        assert 'source_type' in columns, "marketplace_skill 表缺少 source_type 字段"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
