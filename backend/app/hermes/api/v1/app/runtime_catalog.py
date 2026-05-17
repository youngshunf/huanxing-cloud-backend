"""Runtime catalog endpoint surfaced to the WebUI.

PR5 keeps the catalog static — Hermes is the only P0 runtime, and the
WebUI uses this endpoint to populate the Runtime selector when creating
an Agent. Cloud Hermes is intentionally absent (P1 scope per the
hasn-node ↔ hermes-runtime closed-loop plan §A — local Hermes only).

The catalog deliberately does **not** include endpoint or auth values.
Per `01-Hermes RuntimeAdapter接入设计.md` §6, those are `secret://`
references owned exclusively by hasn-node; the backend only knows the
shape of the runtime, not its credentials.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth

router = APIRouter()


_CATALOG: list[dict] = [
    {
        'type': 'hermes',
        'location': 'local',
        'default': True,
        'display_name': 'Hermes (本地)',
        'description': '本地 huanxing-hermes-runtime 进程，A 类工具走本地 MCP socket。',
        'capabilities': {
            'streaming': True,
            'cancel': True,
            'global_context_injection': 'adapter_prompt',
            'mcp_tools': 'local_endpoint',
            'knowledge_tools': 'local_endpoint',
            'skill_injection': 'adapter_mapping',
            'tool_policy_mapping': 'adapter_enforced',
            'dispatch_modes': ['production', 'validation', 'dry_run'],
            'web_entry': True,
        },
    },
]


@router.get('', summary='Runtime 目录', dependencies=[DependsJwtAuth])
async def list_runtime_catalog() -> ResponseModel:
    """Returns the static runtime catalog for the WebUI Agent-create flow.

    The endpoint is JWT-protected (any authenticated user may read it);
    the response carries no user-specific state.
    """
    return response_base.success(data={'items': _CATALOG})
