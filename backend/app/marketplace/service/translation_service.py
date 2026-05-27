"""
Translation Service for Marketplace Skills

Provides automatic translation between English and Chinese using LLM.
"""
import re
from typing import Literal
from langdetect import detect, LangDetectException

from backend.common.log import log
from backend.core.conf import settings


class TranslationService:
    """Translation service for marketplace content"""

    def __init__(self):
        self._translation_cache = {}  # Simple in-memory cache

    def detect_language(self, text: str) -> Literal['en', 'zh', 'unknown']:
        """
        Detect language of text

        Args:
            text: Text to detect

        Returns:
            'en', 'zh', or 'unknown'
        """
        if not text or not text.strip():
            return 'unknown'

        try:
            # Use langdetect library
            lang = detect(text)

            # Map to our supported languages
            if lang in ['en']:
                return 'en'
            elif lang in ['zh-cn', 'zh-tw', 'zh']:
                return 'zh'
            else:
                # Fallback: check for Chinese characters
                if re.search(r'[一-鿿]', text):
                    return 'zh'
                return 'en'  # Default to English

        except LangDetectException:
            # Fallback: check for Chinese characters
            if re.search(r'[一-鿿]', text):
                return 'zh'
            return 'en'

    async def translate(
        self,
        text: str,
        source_lang: Literal['en', 'zh'] | None = None,
        target_lang: Literal['en', 'zh'] = 'zh'
    ) -> str:
        """
        Translate text using LLM

        Args:
            text: Text to translate
            source_lang: Source language (auto-detect if None)
            target_lang: Target language

        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text

        # Auto-detect source language if not provided
        if source_lang is None:
            source_lang = self.detect_language(text)
            if source_lang == 'unknown':
                log.warning(f"Could not detect language for text: {text[:50]}...")
                return text

        # Skip translation if source and target are the same
        if source_lang == target_lang:
            return text

        # Check cache
        cache_key = f"{source_lang}:{target_lang}:{hash(text)}"
        if cache_key in self._translation_cache:
            return self._translation_cache[cache_key]

        # Translate using LLM
        try:
            translated = await self._translate_with_llm(text, source_lang, target_lang)

            # Cache the result
            self._translation_cache[cache_key] = translated

            return translated

        except Exception as e:
            log.error(f"Translation failed: {e}")
            return text  # Return original text on error

    async def _translate_with_llm(
        self,
        text: str,
        source_lang: Literal['en', 'zh'],
        target_lang: Literal['en', 'zh']
    ) -> str:
        """
        Translate text using LLM API directly

        Args:
            text: Text to translate
            source_lang: Source language
            target_lang: Target language

        Returns:
            Translated text
        """
        import httpx

        # Prepare prompt
        lang_names = {'en': 'English', 'zh': 'Chinese'}
        source_name = lang_names[source_lang]
        target_name = lang_names[target_lang]

        prompt = f"""Translate the following {source_name} text to {target_name}.
Keep the translation natural and concise. Only return the translated text, no explanations.

Text to translate:
{text}

Translation:"""

        # Get LLM configuration
        api_base = getattr(settings, 'LLM_API_BASE_URL', 'http://127.0.0.1:3180')
        if not api_base.endswith('/v1'):
            api_base = f"{api_base}/v1"
        api_key = getattr(settings, 'LLM_API_KEY', 'sk-system-translation')
        model = getattr(settings, 'TRANSLATION_MODEL', 'gpt-4o-mini')

        # Call LLM API directly via HTTP
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{api_base}/chat/completions",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a professional translator."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1000,
                    "stream": False
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
            )

            if response.status_code != 200:
                log.error(f"LLM API error: {response.status_code} - {response.text}")
                raise Exception(f"LLM API error: {response.status_code}")

            result = response.json()

            # Check if we got a valid response
            if 'choices' not in result or not result['choices']:
                log.error(f"Invalid LLM response: {result}")
                raise Exception("Invalid LLM response: no choices")

            translated = result['choices'][0]['message']['content'].strip()
            return translated

    async def translate_skill_metadata(
        self,
        name: str | None = None,
        description: str | None = None,
        source_lang: Literal['en', 'zh'] | None = None
    ) -> dict[str, str]:
        """
        Translate skill name and description to both languages

        Args:
            name: Skill name
            description: Skill description
            source_lang: Source language (auto-detect if None, only used for name)

        Returns:
            Dict with keys: name_en, name_zh, description_en, description_zh, source_language
        """
        result = {
            'name_en': None,
            'name_zh': None,
            'description_en': None,
            'description_zh': None,
            'source_language': None
        }

        # Detect source language from name
        if source_lang is None and name:
            source_lang = self.detect_language(name)
        elif source_lang is None:
            source_lang = 'en'  # Default

        result['source_language'] = source_lang

        # Translate name
        if name:
            name_lang = source_lang
            if name_lang == 'en':
                result['name_en'] = name
                translated_name = await self.translate(name, 'en', 'zh')
                # 如果翻译失败（返回原文），则设置为 None
                result['name_zh'] = translated_name if translated_name != name else None
            else:
                result['name_zh'] = name
                translated_name = await self.translate(name, 'zh', 'en')
                # 如果翻译失败（返回原文），则设置为 None
                result['name_en'] = translated_name if translated_name != name else None

        # Translate description (detect language separately)
        if description:
            # Detect description language independently
            desc_lang = self.detect_language(description)

            if desc_lang == 'en':
                result['description_en'] = description
                translated_desc = await self.translate(description, 'en', 'zh')
                # 如果翻译失败（返回原文），则设置为 None
                result['description_zh'] = translated_desc if translated_desc != description else None
            else:
                result['description_zh'] = description
                translated_desc = await self.translate(description, 'zh', 'en')
                # 如果翻译失败（返回原文），则设置为 None
                result['description_en'] = translated_desc if translated_desc != description else None

        return result

    async def batch_translate(
        self,
        texts: list[str],
        source_lang: Literal['en', 'zh'],
        target_lang: Literal['en', 'zh']
    ) -> list[str]:
        """
        Batch translate multiple texts (optimized for efficiency)

        Args:
            texts: List of texts to translate
            source_lang: Source language
            target_lang: Target language

        Returns:
            List of translated texts
        """
        if not texts:
            return []

        # For now, translate one by one
        # TODO: Optimize by batching multiple texts in one LLM call
        results = []
        for text in texts:
            translated = await self.translate(text, source_lang, target_lang)
            results.append(translated)

        return results


# Singleton instance
translation_service = TranslationService()
