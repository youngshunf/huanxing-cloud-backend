"""测试单个技能的翻译"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from backend.app.marketplace.service.translation_service import translation_service
from backend.core.conf import settings

async def test_translation():
    print("测试翻译服务...")

    # 测试中文翻译
    result = await translation_service.translate_skill_metadata(
        name="邮件写作",
        description="商务邮件撰写、回复建议、语气调整"
    )

    print(f"\n翻译结果:")
    print(f"  source_language: {result.get('source_language')}")
    print(f"  name_en: {result.get('name_en')}")
    print(f"  name_zh: {result.get('name_zh')}")
    print(f"  description_en: {result.get('description_en')}")
    print(f"  description_zh: {result.get('description_zh')}")

if __name__ == '__main__':
    asyncio.run(test_translation())
