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
        self.llm_client = None  # Will be initialized when needed
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
        Translate text using LLM API

        Args:
            text: Text to translate
            source_lang: Source language
            target_lang: Target language

        Returns:
            Translated text
        """
        # Import here to avoid circular dependency
        from openai import AsyncOpenAI

        # Initialize client if needed
        if self.llm_client is None:
            self.llm_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=getattr(settings, 'OPENAI_API_BASE', None)
            )

        # Prepare prompt
        lang_names = {'en': 'English', 'zh': 'Chinese'}
        source_name = lang_names[source_lang]
        target_name = lang_names[target_lang]

        prompt = f"""Translate the following {source_name} text to {target_name}.
Keep the translation natural and concise. Only return the translated text, no explanations.

Text to translate:
{text}

Translation:"""

        # Call LLM
        response = await self.llm_client.chat.completions.create(
            model=getattr(settings, 'TRANSLATION_MODEL', 'gpt-4o-mini'),
            messages=[
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )

        translated = response.choices[0].message.content.strip()
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
            source_lang: Source language (auto-detect if None)

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

        # Detect source language from name or description
        if source_lang is None:
            if name:
                source_lang = self.detect_language(name)
            elif description:
                source_lang = self.detect_language(description)
            else:
                source_lang = 'en'  # Default

        result['source_language'] = source_lang

        # Translate name
        if name:
            if source_lang == 'en':
                result['name_en'] = name
                result['name_zh'] = await self.translate(name, 'en', 'zh')
            else:
                result['name_zh'] = name
                result['name_en'] = await self.translate(name, 'zh', 'en')

        # Translate description
        if description:
            if source_lang == 'en':
                result['description_en'] = description
                result['description_zh'] = await self.translate(description, 'en', 'zh')
            else:
                result['description_zh'] = description
                result['description_en'] = await self.translate(description, 'zh', 'en')

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
