from __future__ import annotations

import base64
import re

from backend.common.exception import errors

PUBLISHED_STATUS = 'published'
PUBLIC_VISIBILITY = 'public'
MAX_RESOURCE_ID_LENGTH = 255
MAX_SLUG_LENGTH = 100
MAX_VERSION_LENGTH = 50

_SLUG_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,99}\Z')
_VERSION_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9._+-]{0,49}\Z')
_SLUGIFY_RE = re.compile(r'[^A-Za-z0-9._-]+')


def parse_resource_id(resource_id: str) -> tuple[str, str]:
    """Split "{namespace}/{slug}" by the last slash so namespace may contain slashes."""
    normalized = resource_id.strip('/')
    if len(normalized) > MAX_RESOURCE_ID_LENGTH:
        raise errors.RequestError(msg='资源 ID 过长')
    if '/' not in normalized:
        raise errors.RequestError(msg='资源 ID 必须为 {namespace}/{slug}')
    namespace, slug = normalized.rsplit('/', 1)
    if not namespace or not slug:
        raise errors.RequestError(msg=f'资源 ID 必须为 {namespace}/{slug}')
    return namespace, slug


def build_resource_id(namespace: str, slug: str) -> str:
    resource_id = f'{namespace.strip("/")}/{validate_slug(slug)}'
    if len(resource_id) > MAX_RESOURCE_ID_LENGTH:
        raise errors.RequestError(msg='资源 ID 过长')
    return resource_id


def validate_slug(slug: str) -> str:
    normalized = str(slug).strip().strip('/')
    if (
        not normalized
        or normalized in {'.', '..'}
        or '/' in normalized
        or '\\' in normalized
        or not _SLUG_RE.fullmatch(normalized)
    ):
        raise errors.RequestError(msg='slug 只能包含字母、数字、点、下划线和中划线，且不能包含路径分隔符')
    return normalized


def slug_from_candidate(candidate: str | None, fallback: str) -> str:
    source = str(candidate or fallback).replace('\\', '/').rsplit('/', 1)[-1]
    source = source.rsplit('.', 1)[0] if '.' in source else source
    slug = _SLUGIFY_RE.sub('-', source.strip()).strip('.-_')
    return validate_slug(slug or fallback)


def validate_version(version: str) -> str:
    normalized = str(version).strip()
    if (
        not normalized
        or normalized in {'.', '..'}
        or '/' in normalized
        or '\\' in normalized
        or not _VERSION_RE.fullmatch(normalized)
    ):
        raise errors.RequestError(msg='version 只能包含字母、数字、点、下划线、中划线和加号，且不能包含路径分隔符')
    return normalized


def safe_icon_filename(filename: str | None) -> str:
    raw_name = str(filename or 'icon.svg').replace('\\', '/').rsplit('/', 1)[-1].lower()
    if raw_name.endswith('.svg'):
        return 'icon.svg'
    if raw_name.endswith('.png'):
        return 'icon.png'
    if raw_name.endswith('.jpg'):
        return 'icon.jpg'
    if raw_name.endswith('.jpeg'):
        return 'icon.jpeg'
    raise errors.RequestError(msg='图标仅支持 svg/png/jpg/jpeg')


def encode_namespace(namespace: str) -> str:
    return base64.urlsafe_b64encode(namespace.encode('utf-8')).decode('ascii').rstrip('=')
