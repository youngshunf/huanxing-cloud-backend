"""
Search Service for Marketplace Skills

Provides search and browse functionality for skills.
"""
from typing import Any

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.marketplace.model.marketplace_skill import MarketplaceSkill
from backend.common.log import log


class SearchService:
    """Search service for marketplace skills"""

    async def search_skills(
        self,
        db: AsyncSession,
        keyword: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
        lang: str = 'zh',
        page: int = 1,
        page_size: int = 20,
        sort_by: str = 'popular'
    ) -> dict[str, Any]:
        """
        Search skills with filters

        Args:
            db: Database session
            keyword: Search keyword
            category: Category filter
            tags: Tag filters
            lang: Language (zh/en)
            page: Page number (1-indexed)
            page_size: Items per page
            sort_by: Sort method (popular/latest/downloads/stars)

        Returns:
            Dict with skills list and pagination info
        """
        # Build query
        query = select(MarketplaceSkill).where(MarketplaceSkill.is_private == False)

        # Keyword search
        if keyword:
            if lang == 'zh':
                query = query.where(
                    or_(
                        MarketplaceSkill.name_zh.ilike(f'%{keyword}%'),
                        MarketplaceSkill.description_zh.ilike(f'%{keyword}%')
                    )
                )
            else:
                query = query.where(
                    or_(
                        MarketplaceSkill.name_en.ilike(f'%{keyword}%'),
                        MarketplaceSkill.description_en.ilike(f'%{keyword}%')
                    )
                )

        # Category filter
        if category:
            query = query.where(MarketplaceSkill.category == category)

        # Tags filter
        if tags:
            for tag in tags:
                query = query.where(MarketplaceSkill.tags.contains(tag))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # Sort
        if sort_by == 'latest':
            query = query.order_by(desc(MarketplaceSkill.created_time))
        elif sort_by == 'downloads':
            query = query.order_by(desc(MarketplaceSkill.download_count))
        elif sort_by == 'stars':
            query = query.order_by(desc(MarketplaceSkill.star_count))
        else:  # popular (default)
            # Popular = weighted score of downloads and stars
            query = query.order_by(
                desc(MarketplaceSkill.download_count + MarketplaceSkill.star_count * 10)
            )

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Execute query
        result = await db.execute(query)
        skills = result.scalars().all()

        # Format results
        items = [self._format_skill(skill, lang) for skill in skills]

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    async def get_skill_detail(
        self,
        db: AsyncSession,
        skill_id: str,
        lang: str = 'zh'
    ) -> dict[str, Any] | None:
        """
        Get skill detail by ID (supports both 'namespace/slug' and direct skill_id)

        Args:
            db: Database session
            skill_id: Skill ID (can be 'namespace/slug' or direct skill_id)
            lang: Language (zh/en)

        Returns:
            Skill detail dict or None
        """
        # Try to parse namespace/slug format
        if '/' in skill_id:
            namespace, slug = skill_id.split('/', 1)
            query = select(MarketplaceSkill).where(
                and_(
                    MarketplaceSkill.namespace == namespace,
                    MarketplaceSkill.slug == slug,
                    MarketplaceSkill.is_private == False
                )
            )
        else:
            # Fallback to direct skill_id match
            query = select(MarketplaceSkill).where(
                and_(
                    MarketplaceSkill.skill_id == skill_id,
                    MarketplaceSkill.is_private == False
                )
            )

        result = await db.execute(query)
        skill = result.scalar_one_or_none()

        if not skill:
            return None

        return self._format_skill(skill, lang, detailed=True)

    async def get_popular_skills(
        self,
        db: AsyncSession,
        lang: str = 'zh',
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Get popular skills

        Args:
            db: Database session
            lang: Language (zh/en)
            limit: Number of skills to return

        Returns:
            List of popular skills
        """
        query = (
            select(MarketplaceSkill)
            .where(MarketplaceSkill.is_private == False)
            .order_by(desc(MarketplaceSkill.download_count + MarketplaceSkill.star_count * 10))
            .limit(limit)
        )

        result = await db.execute(query)
        skills = result.scalars().all()

        return [self._format_skill(skill, lang) for skill in skills]

    async def get_official_skills(
        self,
        db: AsyncSession,
        lang: str = 'zh',
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Get official skills

        Args:
            db: Database session
            lang: Language (zh/en)
            limit: Number of skills to return

        Returns:
            List of official skills
        """
        query = (
            select(MarketplaceSkill)
            .where(
                and_(
                    MarketplaceSkill.is_official == True,
                    MarketplaceSkill.is_private == False
                )
            )
            .order_by(desc(MarketplaceSkill.created_time))
            .limit(limit)
        )

        result = await db.execute(query)
        skills = result.scalars().all()

        return [self._format_skill(skill, lang) for skill in skills]

    async def get_categories(self, db: AsyncSession, lang: str = 'zh') -> list[dict[str, Any]]:
        """
        Get all categories with skill counts

        Args:
            db: Database session
            lang: Language (zh/en)

        Returns:
            List of categories
        """
        query = (
            select(
                MarketplaceSkill.category,
                func.count(MarketplaceSkill.id).label('count')
            )
            .where(MarketplaceSkill.is_private == False)
            .group_by(MarketplaceSkill.category)
            .order_by(desc('count'))
        )

        result = await db.execute(query)
        categories = result.all()

        return [
            {
                'category': cat.category,
                'count': cat.count
            }
            for cat in categories
        ]

    def _format_skill(self, skill: MarketplaceSkill, lang: str = 'zh', detailed: bool = False) -> dict[str, Any]:
        """
        Format skill model to dict

        Args:
            skill: Skill model instance
            lang: Language (zh/en)
            detailed: Include detailed info

        Returns:
            Formatted skill dict
        """
        # Choose language fields
        name = skill.name_zh if lang == 'zh' else skill.name_en
        description = skill.description_zh if lang == 'zh' else skill.description_en

        # Fallback to other language if not available
        if not name:
            name = skill.name_en if lang == 'zh' else skill.name_zh
        if not description:
            description = skill.description_en if lang == 'zh' else skill.description_zh

        result = {
            'skill_id': skill.skill_id,
            'namespace': skill.namespace,
            'slug': skill.slug,
            'name': name,
            'description': description,
            'icon_url': skill.icon_url,
            'emoji': skill.emoji,
            'author_name': skill.author_name,
            'category': skill.category,
            'tags': skill.tags,
            'latest_version': skill.latest_version,
            'download_count': skill.download_count,
            'star_count': skill.star_count,
            'is_official': skill.is_official,
            'pricing_type': skill.pricing_type,
            'price': float(skill.price) if skill.price else 0,
            'source_type': skill.source_type,
            'created_time': skill.created_time.isoformat() if skill.created_time else None,
            'updated_time': skill.updated_time.isoformat() if skill.updated_time else None
        }

        if detailed:
            # Add detailed info
            result.update({
                'source_repo_url': skill.source_repo_url,
                'source_repo_path': skill.source_repo_path,
                'repo_path': skill.repo_path,
                'git_commit_hash': skill.git_commit_hash,
                'synced_at': skill.synced_at.isoformat() if skill.synced_at else None,
                'translated_at': skill.translated_at.isoformat() if skill.translated_at else None
            })

        return result


# Singleton instance
search_service = SearchService()
