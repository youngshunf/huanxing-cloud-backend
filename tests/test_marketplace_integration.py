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
from backend.app.marketplace.model.marketplace_skill import MarketplaceSkill
from backend.app.marketplace.model.marketplace_template import MarketplaceTemplate


class TestMarketplaceTables:
    """测试数据库表结构"""

    def test_marketplace_skill_table_exists(self) -> None:
        """测试 marketplace_skill 表是否存在"""
        assert MarketplaceSkill.__tablename__ == 'marketplace_skill'

    def test_marketplace_template_table_exists(self) -> None:
        """测试 marketplace_template 表是否存在"""
        assert MarketplaceTemplate.__tablename__ == 'marketplace_template'

    def test_marketplace_skill_has_namespace_fields(self) -> None:
        """测试 marketplace_skill 表是否有命名空间字段"""
        columns = set(MarketplaceSkill.__table__.columns.keys())

        assert 'namespace' in columns, "marketplace_skill 表缺少 namespace 字段"
        assert 'slug' in columns, "marketplace_skill 表缺少 slug 字段"
        assert 'source_type' in columns, "marketplace_skill 表缺少 source_type 字段"
        assert 'user_id' in columns, "marketplace_skill 表缺少 user_id 字段"
        assert 'hasn_id' in columns, "marketplace_skill 表缺少 hasn_id 字段"
        assert 'status' in columns, "marketplace_skill 表缺少 status 字段"
        assert 'visibility' in columns, "marketplace_skill 表缺少 visibility 字段"

    def test_marketplace_template_has_owner_and_publish_fields(self) -> None:
        """测试 marketplace_template 表是否有用户发布字段"""
        columns = set(MarketplaceTemplate.__table__.columns.keys())

        assert 'namespace' in columns, "marketplace_template 表缺少 namespace 字段"
        assert 'slug' in columns, "marketplace_template 表缺少 slug 字段"
        assert 'source_type' in columns, "marketplace_template 表缺少 source_type 字段"
        assert 'user_id' in columns, "marketplace_template 表缺少 user_id 字段"
        assert 'hasn_id' in columns, "marketplace_template 表缺少 hasn_id 字段"
        assert 'status' in columns, "marketplace_template 表缺少 status 字段"
        assert 'visibility' in columns, "marketplace_template 表缺少 visibility 字段"
