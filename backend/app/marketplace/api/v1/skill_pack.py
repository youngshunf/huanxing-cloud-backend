from __future__ import annotations

import hashlib
from decimal import Decimal
from typing import Any

import sqlalchemy as sa
from fastapi import APIRouter, Request

from backend.app.marketplace.schema.skill_pack import SkillPackCreateRequest, SkillPackResponse
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('', summary='List marketplace skill packs')
async def list_skill_packs(request: Request, db: CurrentSession) -> ResponseSchemaModel[list[SkillPackResponse]]:
    user_id = getattr(request.scope.get('user'), 'id', None)
    result = await db.execute(
        sa.text(
            '''
            SELECT
                t.template_id,
                t.name,
                t.description,
                v.version,
                v.bundle_slug,
                v.command_key,
                v.hermes_bundle_json,
                v.hermes_yaml,
                COALESCE(v.content_hash, v.file_hash) AS content_hash,
                v.package_url,
                v.file_hash,
                v.published_at
            FROM public.marketplace_template t
            JOIN public.marketplace_template_version v
              ON v.template_id = t.template_id
             AND v.is_latest = true
            WHERE t.template_type = 'skill_pack'
              AND (
                t.is_private = false
                OR t.is_official = true
                OR t.author_id = :user_id
              )
              AND v.bundle_slug IS NOT NULL
              AND v.command_key IS NOT NULL
              AND v.hermes_yaml IS NOT NULL
            ORDER BY t.is_official DESC, t.download_count DESC, t.id DESC
            '''
        ),
        {'user_id': user_id},
    )
    return response_base.success(data=[_skill_pack_response(dict(row)) for row in result.mappings().all()])


@router.post('', summary='Create or update marketplace skill pack', dependencies=[DependsJwtAuth])
async def create_skill_pack(
    request: Request,
    db: CurrentSessionTransaction,
    payload: SkillPackCreateRequest,
) -> ResponseSchemaModel[SkillPackResponse]:
    template_id = payload.template_id or _template_id(payload.namespace, payload.bundle_slug)
    now_hash = payload.content_hash or _content_hash(payload.hermes_yaml)
    await db.execute(
        sa.text(
            '''
            INSERT INTO public.marketplace_template (
                template_id,
                namespace,
                slug,
                template_type,
                name,
                description,
                author_id,
                pricing_type,
                price,
                is_private,
                is_official,
                download_count,
                source_type,
                created_time,
                updated_time
            ) VALUES (
                :template_id,
                :namespace,
                :slug,
                'skill_pack',
                :name,
                :description,
                :author_id,
                'free',
                :price,
                :is_private,
                :is_official,
                0,
                'local',
                now(),
                now()
            )
            ON CONFLICT (template_id) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                is_private = EXCLUDED.is_private,
                is_official = EXCLUDED.is_official,
                updated_time = now()
            '''
        ),
        {
            'template_id': template_id,
            'namespace': payload.namespace,
            'slug': payload.bundle_slug,
            'name': payload.name,
            'description': payload.description,
            'author_id': getattr(request.scope.get('user'), 'id', None),
            'price': Decimal('0'),
            'is_private': payload.is_private,
            'is_official': payload.is_official,
        },
    )
    await db.execute(
        sa.text(
            '''
            UPDATE public.marketplace_template_version
            SET is_latest = false,
                updated_time = now()
            WHERE template_id = :template_id
            '''
        ),
        {'template_id': template_id},
    )
    await db.execute(
        sa.text(
            '''
            INSERT INTO public.marketplace_template_version (
                template_id,
                version,
                changelog,
                skill_dependencies_versioned,
                bundle_slug,
                command_key,
                hermes_bundle_json,
                hermes_yaml,
                content_hash,
                file_hash,
                is_latest,
                published_at,
                created_time,
                updated_time
            ) VALUES (
                :template_id,
                :version,
                NULL,
                CAST(:skill_dependencies_versioned AS jsonb),
                :bundle_slug,
                :command_key,
                CAST(:hermes_bundle_json AS jsonb),
                :hermes_yaml,
                :content_hash,
                :content_hash,
                true,
                now(),
                now(),
                now()
            )
            ON CONFLICT (template_id, version) DO UPDATE SET
                skill_dependencies_versioned = EXCLUDED.skill_dependencies_versioned,
                bundle_slug = EXCLUDED.bundle_slug,
                command_key = EXCLUDED.command_key,
                hermes_bundle_json = EXCLUDED.hermes_bundle_json,
                hermes_yaml = EXCLUDED.hermes_yaml,
                content_hash = EXCLUDED.content_hash,
                file_hash = EXCLUDED.file_hash,
                is_latest = true,
                published_at = EXCLUDED.published_at,
                updated_time = now()
            '''
        ),
        {
            'template_id': template_id,
            'version': payload.version,
            'skill_dependencies_versioned': _json(payload.skill_dependencies_versioned),
            'bundle_slug': payload.bundle_slug,
            'command_key': payload.command_key,
            'hermes_bundle_json': _json(payload.hermes_bundle_json),
            'hermes_yaml': payload.hermes_yaml,
            'content_hash': now_hash,
        },
    )
    return response_base.success(
        data=SkillPackResponse(
            template_id=template_id,
            version=payload.version,
            name=payload.name,
            description=payload.description,
            bundle_slug=payload.bundle_slug,
            command_key=payload.command_key,
            hermes_bundle_json=payload.hermes_bundle_json,
            hermes_yaml=payload.hermes_yaml,
            content_hash=now_hash,
            file_hash=now_hash,
        )
    )


def _skill_pack_response(row: dict[str, Any]) -> SkillPackResponse:
    return SkillPackResponse(
        template_id=row['template_id'],
        version=row['version'],
        name=row['name'],
        description=row.get('description'),
        bundle_slug=row['bundle_slug'],
        command_key=row['command_key'],
        hermes_bundle_json=row.get('hermes_bundle_json'),
        hermes_yaml=row['hermes_yaml'],
        content_hash=row['content_hash'],
        package_url=row.get('package_url'),
        file_hash=row.get('file_hash'),
        published_at=row.get('published_at'),
    )


def _template_id(namespace: str | None, bundle_slug: str) -> str:
    prefix = f'{namespace}/' if namespace else 'skill-pack/'
    return f'{prefix}{bundle_slug}'


def _content_hash(value: str) -> str:
    return f'sha256:{hashlib.sha256(value.encode("utf-8")).hexdigest()}'


def _json(value: Any) -> str:
    import json

    return json.dumps(value or {}, ensure_ascii=False, sort_keys=True)
