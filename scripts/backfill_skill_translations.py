#!/usr/bin/env python3
"""Backfill bilingual translations + bilingual tags + emoji for marketplace skills.

Examples:
    # Re-translate every skill (overwrites fallback-garbage tags, fills emoji)
    uv run python scripts/backfill_skill_translations.py

    # Only rows missing a side / emoji
    uv run python scripts/backfill_skill_translations.py --only-missing

    # A single skill, for a quick check
    uv run python scripts/backfill_skill_translations.py --skill-id clawhub/yonglie/customsdata
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.marketplace.service.skill_translation_backfill_service import backfill_skill_translations
from backend.database.db import async_db_session


async def main() -> None:
    parser = argparse.ArgumentParser(description='Backfill marketplace skill translations')
    parser.add_argument('--only-missing', action='store_true', help='Only rows missing a translated side / emoji')
    parser.add_argument('--limit', type=int, default=None, help='Cap number of rows processed')
    parser.add_argument('--batch-size', type=int, default=10, help='Skills per LLM request')
    parser.add_argument('--concurrency', type=int, default=4, help='Parallel batch requests')
    parser.add_argument('--skill-id', action='append', dest='skill_ids', help='Restrict to skill_id (repeatable)')
    args = parser.parse_args()

    async with async_db_session() as db:
        result = await backfill_skill_translations(
            db,
            only_missing=args.only_missing,
            skill_ids=args.skill_ids,
            limit=args.limit,
            batch_size=args.batch_size,
            concurrency=args.concurrency,
        )

    print('\n=== Backfill result ===')
    for key in ('success', 'total', 'updated', 'failed', 'message'):
        if key in result:
            print(f'  {key}: {result[key]}')
    for err in result.get('errors', []):
        print(f'  error: {err}')


if __name__ == '__main__':
    asyncio.run(main())
