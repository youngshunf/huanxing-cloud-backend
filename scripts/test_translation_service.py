#!/usr/bin/env python3
"""
Test translation service
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.marketplace.service.translation_service import translation_service


async def test_language_detection():
    """Test language detection"""
    print("=" * 60)
    print("测试语言检测")
    print("=" * 60)

    test_cases = [
        ("Hello, world!", "en"),
        ("你好，世界！", "zh"),
        ("This is a test", "en"),
        ("这是一个测试", "zh"),
        ("Professional translation tool", "en"),
        ("专业翻译助手", "zh"),
    ]

    for text, expected in test_cases:
        detected = translation_service.detect_language(text)
        status = "✅" if detected == expected else "❌"
        print(f"{status} '{text}' -> {detected} (expected: {expected})")

    print()


async def test_translation():
    """Test translation"""
    print("=" * 60)
    print("测试翻译功能")
    print("=" * 60)

    # Note: This requires LLM API to be configured
    # For now, we'll just test the interface

    test_cases = [
        ("Hello, world!", "en", "zh"),
        ("你好，世界！", "zh", "en"),
    ]

    for text, source, target in test_cases:
        try:
            translated = await translation_service.translate(text, source, target)
            print(f"✅ {source} -> {target}: '{text}' -> '{translated}'")
        except Exception as e:
            print(f"⚠️  Translation failed (expected if LLM not configured): {e}")

    print()


async def test_skill_metadata_translation():
    """Test skill metadata translation"""
    print("=" * 60)
    print("测试技能元数据翻译")
    print("=" * 60)

    try:
        result = await translation_service.translate_skill_metadata(
            name="Translator Pro",
            description="Professional translation tool with multi-language support",
            source_lang="en"
        )

        print("✅ Skill metadata translation:")
        print(f"  Source Language: {result['source_language']}")
        print(f"  Name EN: {result['name_en']}")
        print(f"  Name ZH: {result['name_zh']}")
        print(f"  Description EN: {result['description_en'][:50]}...")
        print(f"  Description ZH: {result['description_zh'][:50] if result['description_zh'] else 'None'}...")
    except Exception as e:
        print(f"⚠️  Metadata translation failed (expected if LLM not configured): {e}")

    print()


async def main():
    print("\n🔍 Translation Service Test\n")

    # Test 1: Language Detection (no LLM required)
    await test_language_detection()

    # Test 2: Translation (requires LLM)
    await test_translation()

    # Test 3: Skill Metadata Translation (requires LLM)
    await test_skill_metadata_translation()

    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
