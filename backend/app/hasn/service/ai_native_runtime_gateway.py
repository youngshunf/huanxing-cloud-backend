from __future__ import annotations

from typing import TYPE_CHECKING, Any

import sqlalchemy as sa

from fastapi.security.utils import get_authorization_scheme_param

from backend.app.hasn.model import HasnAiNativeAppAudit, HasnWorkspaceApp
from backend.app.hasn.service.ai_native_app_registry import ai_native_app_registry
from backend.app.hasn.service.workbench_domain_service import workbench_domain_service
from backend.app.hasn_community.service.community_service import community_service
from backend.common.exception import errors
from backend.common.security.agent_jwt import jwt_decode_agent
from backend.database.redis import redis_client

if TYPE_CHECKING:
    from backend.app.hasn.schema.ai_native_runtime import (
        AiNativeAuditQuery,
        AiNativeRuntimeCapabilitiesRequest,
        AiNativeToolCallRequest,
    )
    from backend.common.dataclasses import AgentTokenPayload


class _RuntimeDenial(Exception):
    def __init__(self, *, code: str, message: str, workspace: dict[str, Any]) -> None:
        self.code = code
        self.message = message
        self.workspace = workspace


class AiNativeRuntimeGateway:
    async def get_capabilities(self, db, *, request, body: AiNativeRuntimeCapabilitiesRequest) -> dict[str, Any]:
        agent = self._require_agent(request)
        workspace = await self._resolve_workspace(db, agent=agent, requested_workspace=body.workspace)
        manifest = await ai_native_app_registry.ensure_builtin_published(db, 'knowledge')

        tool = manifest['manifest_json']['tools'][0]
        capability = manifest['manifest_json']['capabilities'][0]
        if not await self._is_workspace_app_enabled(db, workspace=workspace, app_id=manifest['app_id']):
            return self._capabilities_payload(workspace=workspace, agent=agent, manifest=manifest, tools=[])
        if not self._can_discover_tool(workspace=workspace, manifest=manifest, capability=capability):
            return self._capabilities_payload(workspace=workspace, agent=agent, manifest=manifest, tools=[])
        if await self._is_tool_denied_by_policy(
            db, agent, tool_name=tool['mcp_name'], required_scopes=tool['required_scopes']
        ):
            return self._capabilities_payload(workspace=workspace, agent=agent, manifest=manifest, tools=[])

        return self._capabilities_payload(
            workspace=workspace,
            agent=agent,
            manifest=manifest,
            tools=[
                {
                    'app_id': manifest['app_id'],
                    'tool_id': tool['tool_id'],
                    'mcp_name': tool['mcp_name'],
                    'collaboration_mode': manifest['collaboration_mode'],
                    'display_name': capability['name'],
                    'input_schema': capability['input_schema'],
                    'output_schema': capability['output_schema'],
                    'required_scopes': tool['required_scopes'],
                    'risk_level': tool['risk_level'],
                    'requires_confirmation': False,
                    'idempotent': tool['idempotent'],
                }
            ],
        )

    def _capabilities_payload(
        self,
        *,
        workspace: dict[str, Any],
        agent: AgentTokenPayload | None,
        manifest: dict[str, Any],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            'workspace': self._workspace_payload(workspace),
            'agent': self._agent_payload(agent),
            'manifest_hash': manifest['manifest_hash'],
            'tools': tools,
        }

    async def call_tool(
        self,
        db,
        *,
        request,
        app_id: str,
        tool_id: str,
        body: AiNativeToolCallRequest,
    ) -> dict[str, Any]:
        agent_result = await self._authenticate_runtime_agent(request)
        if agent_result.get('decision') == 'deny':
            manifest = await ai_native_app_registry.ensure_builtin_published(db, app_id)
            tool = self._find_tool(manifest, tool_id)
            capability = self._find_capability(manifest, tool_id)
            workspace = self._fallback_personal_workspace(agent_result.get('agent'))
            audit = await self._write_audit(
                db,
                trace_id=body.trace_id,
                workspace=workspace,
                agent=agent_result.get('agent'),
                manifest=manifest,
                capability=capability,
                tool=tool,
                decision='deny',
                error_code=agent_result['code'],
                context={'reason': agent_result['message']},
            )
            return self._deny_payload(body.trace_id, agent_result['code'], agent_result['message'], audit_id=audit['id'])

        agent = agent_result['agent']
        try:
            workspace = await self._resolve_workspace(db, agent=agent, requested_workspace=body.workspace)
        except _RuntimeDenial as denial:
            manifest = await ai_native_app_registry.ensure_builtin_published(db, app_id)
            tool = self._find_tool(manifest, tool_id)
            capability = self._find_capability(manifest, tool_id)
            audit = await self._write_audit(
                db,
                trace_id=body.trace_id,
                workspace=denial.workspace,
                agent=agent,
                manifest=manifest,
                capability=capability,
                tool=tool,
                decision='deny',
                error_code=denial.code,
                context={'reason': denial.message},
            )
            return self._deny_payload(body.trace_id, denial.code, denial.message, audit_id=audit['id'])
        manifest = await ai_native_app_registry.ensure_builtin_published(db, app_id)
        tool = self._find_tool(manifest, tool_id)
        capability = self._find_capability(manifest, tool_id)
        if not await self._is_workspace_app_enabled(db, workspace=workspace, app_id=app_id):
            audit = await self._write_audit(
                db,
                trace_id=body.trace_id,
                workspace=workspace,
                agent=agent,
                manifest=manifest,
                capability=capability,
                tool=tool,
                decision='deny',
                error_code='15002',
                context={'reason': 'app_not_enabled'},
            )
            return self._deny_payload(body.trace_id, '15002', 'app_not_enabled', audit_id=audit['id'])

        collaboration_denial = self._collaboration_denial(workspace=workspace, manifest=manifest)
        if collaboration_denial is not None:
            audit = await self._write_audit(
                db,
                trace_id=body.trace_id,
                workspace=workspace,
                agent=agent,
                manifest=manifest,
                capability=capability,
                tool=tool,
                decision='deny',
                error_code='15005',
                context={'reason': collaboration_denial},
            )
            return self._deny_payload(body.trace_id, '15005', collaboration_denial, audit_id=audit['id'])

        required_scopes = list(tool.get('required_scopes') or [])
        if await self._is_tool_denied_by_policy(
            db, agent, tool_name=tool.get('mcp_name') or tool_id, required_scopes=required_scopes
        ):
            audit = await self._write_audit(
                db,
                trace_id=body.trace_id,
                workspace=workspace,
                agent=agent,
                manifest=manifest,
                capability=capability,
                tool=tool,
                decision='deny',
                error_code='15012',
                context={'reason': 'agent_scope_missing'},
            )
            return self._deny_payload(body.trace_id, '15012', 'agent_scope_missing', audit_id=audit['id'])

        role_denial = self._enterprise_role_denial(workspace=workspace, capability=capability)
        if role_denial is not None:
            audit = await self._write_audit(
                db,
                trace_id=body.trace_id,
                workspace=workspace,
                agent=agent,
                manifest=manifest,
                capability=capability,
                tool=tool,
                decision='deny',
                error_code='15004',
                context={'reason': role_denial},
            )
            return self._deny_payload(body.trace_id, '15004', role_denial, audit_id=audit['id'])

        input_payload = dict(body.input or {})
        if not self._valid_tool_input(tool_id, input_payload):
            audit = await self._write_audit(
                db,
                trace_id=body.trace_id,
                workspace=workspace,
                agent=agent,
                manifest=manifest,
                capability=capability,
                tool=tool,
                decision='deny',
                error_code='15020',
                context={'reason': 'input_schema_invalid'},
            )
            return self._deny_payload(body.trace_id, '15020', 'input_schema_invalid', audit_id=audit['id'])

        # 路由到对应的 handler
        if app_id == 'knowledge' and tool_id == 'knowledge.search':
            result = await workbench_domain_service.search_current_knowledge(
                db,
                user_id=agent.owner_user_id,
                query=str(input_payload['query']),
                limit=int(input_payload.get('limit') or 50),
                dataset_id=input_payload.get('dataset_id'),
            )
        elif app_id == 'community' and tool_id == 'community.get_post':
            result = await community_service.get_agent_post_resource(
                db,
                agent=agent,
                post_id=str(input_payload['post_id']),
            )
        elif app_id == 'community' and tool_id == 'community.get_article':
            result = await community_service.get_agent_article_resource(
                db,
                agent=agent,
                article_id=str(input_payload['article_id']),
            )
        elif app_id == 'community' and tool_id == 'community.get_feed':
            from backend.app.hasn_community.service.community_tool_handlers import handle_community_get_feed
            result = await handle_community_get_feed(db, agent, input_payload)
        elif app_id == 'community' and tool_id == 'community.create_post':
            from backend.app.hasn_community.service.community_tool_handlers import handle_community_create_post
            result = await handle_community_create_post(db, agent, input_payload)
        elif app_id == 'community' and tool_id == 'community.create_article':
            from backend.app.hasn_community.service.community_tool_handlers import handle_community_create_article
            result = await handle_community_create_article(db, agent, input_payload)
        else:
            raise errors.NotFoundError(msg='AI-Native 工具不存在')
        audit = await self._write_audit(
            db,
            trace_id=body.trace_id,
            workspace=workspace,
            agent=agent,
            manifest=manifest,
            capability=capability,
            tool=tool,
            decision='allow',
            result_ref=f'{app_id}:{tool_id}:{body.trace_id}',
        )
        return {
            'trace_id': body.trace_id,
            'decision': 'allow',
            'workspace': self._workspace_payload(workspace),
            'app_id': app_id,
            'tool_id': tool_id,
            'result': result,
            'audit_id': audit['id'],
        }

    async def list_audit(self, db, *, query: AiNativeAuditQuery) -> dict[str, Any]:
        stmt = sa.select(HasnAiNativeAppAudit)
        if query.workspace_kind:
            stmt = stmt.where(HasnAiNativeAppAudit.workspace_kind == query.workspace_kind)
        if query.app_id:
            stmt = stmt.where(HasnAiNativeAppAudit.app_id == query.app_id)
        if query.agent_hasn_id:
            stmt = stmt.where(HasnAiNativeAppAudit.agent_hasn_id == query.agent_hasn_id)
        if query.trace_id:
            stmt = stmt.where(HasnAiNativeAppAudit.trace_id == query.trace_id)
        if query.created_at_from:
            stmt = stmt.where(HasnAiNativeAppAudit.created_at >= query.created_at_from)
        if query.created_at_to:
            stmt = stmt.where(HasnAiNativeAppAudit.created_at <= query.created_at_to)
        rows = (await db.execute(stmt.order_by(HasnAiNativeAppAudit.id.desc()))).scalars().all()
        return {'items': [self._audit_payload(row) for row in rows], 'total': len(rows)}

    def _require_agent(self, request) -> AgentTokenPayload:
        agent = getattr(request.state, 'agent', None)
        if agent is None:
            raise errors.TokenError(msg='Agent JWT 未认证')
        return agent

    async def _authenticate_runtime_agent(self, request) -> dict[str, Any]:
        agent = getattr(request.state, 'agent', None)
        if agent is not None:
            return {'decision': 'allow', 'agent': agent}

        authorization = request.headers.get('Authorization') or request.headers.get('authorization')
        scheme, token = get_authorization_scheme_param(authorization)
        if not token or scheme.lower() != 'bearer':
            return {'decision': 'deny', 'code': '15010', 'message': 'agent_jwt_missing', 'agent': None}

        try:
            decoded = jwt_decode_agent(token)
        except errors.TokenError:
            return {'decision': 'deny', 'code': '15010', 'message': 'agent_jwt_invalid', 'agent': None}

        redis_token = await redis_client.get(f'agent_token:{decoded.agent_hasn_id}:{decoded.session_uuid}')
        if not redis_token:
            return {
                'decision': 'deny',
                'code': '15011',
                'message': 'agent_token_session_revoked',
                'agent': decoded,
            }
        if token != redis_token:
            return {
                'decision': 'deny',
                'code': '15011',
                'message': 'agent_token_session_mismatch',
                'agent': decoded,
            }

        request.state.agent = decoded
        return {'decision': 'allow', 'agent': decoded}

    def _fallback_personal_workspace(self, agent: AgentTokenPayload | None) -> dict[str, Any]:
        user_id = agent.owner_user_id if agent is not None else None
        return {
            'kind': 'personal',
            'user_id': user_id,
            'enterprise_id': None,
            'workspace_key': f'personal:{user_id}' if user_id is not None else 'personal:unknown',
        }

    async def _resolve_workspace(
        self,
        db,
        *,
        agent: AgentTokenPayload | None,
        requested_workspace: dict[str, Any] | None,
    ) -> dict[str, Any]:
        workspace = dict(
            requested_workspace
            or await workbench_domain_service.get_active_workspace(db, user_id=agent.owner_user_id)
        )
        kind = workspace.get('kind') or 'personal'
        if kind not in {'personal', 'enterprise'}:
            raise _RuntimeDenial(
                code='15003',
                message='workspace_inaccessible',
                workspace=self._fallback_personal_workspace(agent),
            )
        workspace['kind'] = kind
        if kind == 'personal':
            workspace['user_id'] = agent.owner_user_id
            workspace['enterprise_id'] = None
            workspace['workspace_key'] = f'personal:{agent.owner_user_id}'
            return workspace

        enterprise_id = workspace.get('enterprise_id')
        if enterprise_id is None:
            raise _RuntimeDenial(
                code='15003',
                message='workspace_inaccessible',
                workspace=self._fallback_enterprise_workspace(None),
            )
        membership = await workbench_domain_service._approved_membership(
            db, enterprise_id=int(enterprise_id), user_id=agent.owner_user_id
        )
        if membership is None:
            raise _RuntimeDenial(
                code='15003',
                message='workspace_inaccessible',
                workspace=self._fallback_enterprise_workspace(int(enterprise_id)),
            )
        workspace['user_id'] = None
        workspace['enterprise_id'] = int(enterprise_id)
        workspace['workspace_key'] = f'enterprise:{enterprise_id}'
        workspace['role'] = getattr(membership, 'role', 'member')
        return workspace

    def _fallback_enterprise_workspace(self, enterprise_id: int | None) -> dict[str, Any]:
        return {
            'kind': 'enterprise',
            'user_id': None,
            'enterprise_id': enterprise_id,
            'workspace_key': f'enterprise:{enterprise_id}' if enterprise_id is not None else 'enterprise:unknown',
        }

    async def _ensure_workspace_app_enabled(self, db, *, workspace: dict[str, Any], app_id: str) -> None:
        if not await self._is_workspace_app_enabled(db, workspace=workspace, app_id=app_id):
            raise errors.ForbiddenError(msg='app_not_enabled')

    async def _is_workspace_app_enabled(self, db, *, workspace: dict[str, Any], app_id: str) -> bool:
        row = await self._get_workspace_app(db, workspace=workspace, app_id=app_id)
        return row is not None and row.status == 'active'

    async def _get_workspace_app(self, db, *, workspace: dict[str, Any], app_id: str):
        stmt = sa.select(HasnWorkspaceApp).where(
            HasnWorkspaceApp.workspace_kind == workspace['kind'],
            HasnWorkspaceApp.app_id == app_id,
        )
        if workspace['kind'] == 'personal':
            stmt = stmt.where(HasnWorkspaceApp.user_id == workspace.get('user_id'))
        else:
            stmt = stmt.where(HasnWorkspaceApp.enterprise_id == workspace.get('enterprise_id'))
        return (await db.execute(stmt)).scalars().first()

    def _find_tool(self, manifest: dict[str, Any], tool_id: str) -> dict[str, Any]:
        for tool in manifest['manifest_json'].get('tools') or []:
            if tool.get('tool_id') == tool_id:
                return tool
        raise errors.NotFoundError(msg='AI-Native 工具不存在')

    def _find_capability(self, manifest: dict[str, Any], tool_id: str) -> dict[str, Any]:
        for capability in manifest['manifest_json'].get('capabilities') or []:
            if capability.get('tool_id') == tool_id:
                return capability
        raise errors.NotFoundError(msg='AI-Native 能力不存在')

    async def _is_tool_denied_by_policy(
        self,
        db,
        agent: AgentTokenPayload,
        *,
        tool_name: str,
        required_scopes: list[str],
    ) -> bool:
        """维度① 三态能力授权（D3 活取）：deny → True，allow/ask → False。

        统一走 hasn_agent_scopes 三态策略（default_mode + capability_modes），不再读
        key/JWT 冻结的 scopes 快照（D3：快照仅供审计、不作判定依据），因此也不受 key
        快照词表点号/冒号不一致影响。默认 allow（所有工具一视同仁）。ask 不在此挂起——
        交由 MCP server.call_tool 的 ask 闸门处理，本门只硬拦 deny。
        """
        from backend.common.security.agent_jwt import get_agent_scopes_cached
        from backend.common.security.scope_policy import MODE_DENY, resolve_tool_mode

        policy = await get_agent_scopes_cached(agent.agent_hasn_id, db)
        mode = resolve_tool_mode(
            policy.get('default_mode', 'allow'),
            policy.get('capability_modes'),
            tool_name=tool_name,
            required_scopes=list(required_scopes or []),
        )
        return mode == MODE_DENY

    def _can_discover_tool(
        self,
        *,
        workspace: dict[str, Any],
        manifest: dict[str, Any],
        capability: dict[str, Any],
    ) -> bool:
        manifest_json = manifest.get('manifest_json') or {}
        workspace_scope = set(manifest.get('workspace_scope') or manifest_json.get('workspace_scope') or [])
        if workspace_scope and workspace['kind'] not in workspace_scope:
            return False
        if self._collaboration_denial(workspace=workspace, manifest=manifest) is not None:
            return False
        return self._enterprise_role_denial(workspace=workspace, capability=capability) is None

    def _collaboration_denial(self, *, workspace: dict[str, Any], manifest: dict[str, Any]) -> str | None:
        if workspace['kind'] != 'enterprise':
            return None
        manifest_json = manifest.get('manifest_json') or {}
        collaboration_mode = str(manifest.get('collaboration_mode') or manifest_json.get('collaboration_mode') or 'none')
        if collaboration_mode != 'workspace_shared':
            return 'app_not_support_enterprise_collaboration'
        return None

    def _enterprise_role_denial(self, *, workspace: dict[str, Any], capability: dict[str, Any]) -> str | None:
        if workspace['kind'] != 'enterprise':
            return None
        workspace_roles = set(capability.get('workspace_roles') or [])
        if workspace_roles and self._workspace_role(workspace) not in workspace_roles:
            return 'enterprise_role_insufficient'
        return None

    def _workspace_role(self, workspace: dict[str, Any]) -> str:
        return workspace.get('role') or ('owner' if workspace['kind'] == 'personal' else 'member')

    def _valid_search_input(self, data: dict[str, Any]) -> bool:
        query = data.get('query')
        if not isinstance(query, str) or not query.strip():
            return False
        if 'limit' in data and data['limit'] is not None:
            try:
                limit = int(data['limit'])
            except (TypeError, ValueError):
                return False
            if limit < 1 or limit > 50:
                return False
        dataset_id = data.get('dataset_id')
        return dataset_id is None or isinstance(dataset_id, str)

    def _valid_tool_input(self, tool_id: str, data: dict[str, Any]) -> bool:
        if tool_id == 'knowledge.search':
            return self._valid_search_input(data)
        if tool_id == 'community.get_feed':
            feed_type = data.get('type')
            if not isinstance(feed_type, str) or feed_type not in {'following', 'recommend', 'hot', 'articles'}:
                return False
            return self._valid_limit(data, default_max=50)
        if tool_id == 'community.get_post':
            post_id = data.get('post_id')
            return isinstance(post_id, str) and bool(post_id.strip())
        if tool_id == 'community.get_article':
            article_id = data.get('article_id')
            return isinstance(article_id, str) and bool(article_id.strip())
        if tool_id == 'community.create_post':
            content = data.get('content')
            return isinstance(content, str) and bool(content.strip()) and len(content) <= 10000
        if tool_id == 'community.create_article':
            title = data.get('title')
            content = data.get('content')
            return (
                isinstance(title, str)
                and bool(title.strip())
                and len(title) <= 200
                and isinstance(content, str)
                and bool(content.strip())
                and len(content) <= 100000
            )
        return True

    def _valid_limit(self, data: dict[str, Any], *, default_max: int) -> bool:
        if 'limit' not in data or data['limit'] is None:
            return True
        try:
            limit = int(data['limit'])
        except (TypeError, ValueError):
            return False
        return 1 <= limit <= default_max

    def _deny_payload(self, trace_id: str, code: str, message: str, *, audit_id: int) -> dict[str, Any]:
        return {
            'trace_id': trace_id,
            'decision': 'deny',
            'error': {'code': code, 'message': message},
            'audit_id': audit_id,
        }

    async def _write_audit(
        self,
        db,
        *,
        trace_id: str,
        workspace: dict[str, Any],
        agent: AgentTokenPayload,
        manifest: dict[str, Any],
        capability: dict[str, Any],
        tool: dict[str, Any],
        decision: str,
        error_code: str | None = None,
        result_ref: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        row = HasnAiNativeAppAudit(
            trace_id=trace_id,
            step='runtime',
            workspace_kind=workspace['kind'],
            user_id=workspace.get('user_id'),
            enterprise_id=workspace.get('enterprise_id'),
            app_id=manifest['app_id'],
            app_version=manifest['version'],
            actor_type='agent',
            agent_hasn_id=agent.agent_hasn_id if agent is not None else None,
            owner_hasn_id=agent.owner_hasn_id if agent is not None else None,
            session_uuid=agent.session_uuid if agent is not None else None,
            method='tool_call',
            capability_id=capability.get('capability_id'),
            tool_id=tool.get('tool_id'),
            event_type='tool_call',
            required_scopes=list(tool.get('required_scopes') or []),
            agent_scopes_snapshot=list(agent.scopes) if agent is not None else [],
            workspace_role=self._workspace_role(workspace),
            risk_level=tool.get('risk_level'),
            decision=decision,
            confirmation_id=None,
            result_ref=result_ref,
            error_code=error_code,
            context=context or {},
        )
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return self._audit_payload(row)

    def _workspace_payload(self, workspace: dict[str, Any]) -> dict[str, Any]:
        return {
            'kind': workspace['kind'],
            'user_id': workspace.get('user_id'),
            'enterprise_id': workspace.get('enterprise_id'),
            'workspace_key': workspace['workspace_key'],
        }

    def _agent_payload(self, agent: AgentTokenPayload) -> dict[str, Any]:
        return {
            'agent_hasn_id': agent.agent_hasn_id,
            'owner_hasn_id': agent.owner_hasn_id,
            'session_uuid': agent.session_uuid,
        }

    def _audit_payload(self, row: HasnAiNativeAppAudit) -> dict[str, Any]:
        return {
            'id': row.id,
            'trace_id': row.trace_id,
            'step': row.step,
            'workspace_kind': row.workspace_kind,
            'user_id': row.user_id,
            'enterprise_id': row.enterprise_id,
            'app_id': row.app_id,
            'app_version': row.app_version,
            'actor_type': row.actor_type,
            'agent_hasn_id': row.agent_hasn_id,
            'owner_hasn_id': row.owner_hasn_id,
            'session_uuid': row.session_uuid,
            'method': row.method,
            'capability_id': row.capability_id,
            'tool_id': row.tool_id,
            'event_type': row.event_type,
            'required_scopes': row.required_scopes,
            'agent_scopes_snapshot': row.agent_scopes_snapshot,
            'workspace_role': row.workspace_role,
            'risk_level': row.risk_level,
            'decision': row.decision,
            'confirmation_id': row.confirmation_id,
            'result_ref': row.result_ref,
            'error_code': row.error_code,
            'context': row.context,
            'created_at': row.created_at,
        }


ai_native_runtime_gateway: AiNativeRuntimeGateway = AiNativeRuntimeGateway()
