from __future__ import annotations

from typing import Any

import sqlalchemy as sa

from backend.app.hasn.model import HasnAiNativeAppAudit, HasnWorkspaceApp
from backend.app.hasn.schema.ai_native_runtime import (
    AiNativeAuditQuery,
    AiNativeRuntimeCapabilitiesRequest,
    AiNativeToolCallRequest,
)
from backend.app.hasn.service.ai_native_app_registry import ai_native_app_registry
from backend.app.hasn.service.workbench_domain_service import workbench_domain_service
from backend.common.dataclasses import AgentTokenPayload
from backend.common.exception import errors


class AiNativeRuntimeGateway:
    async def get_capabilities(self, db, *, request, body: AiNativeRuntimeCapabilitiesRequest) -> dict[str, Any]:
        agent = self._require_agent(request)
        workspace = await self._resolve_workspace(db, agent=agent, requested_workspace=body.workspace)
        manifest = await ai_native_app_registry.ensure_builtin_published(db, 'knowledge')

        tool = manifest['manifest_json']['tools'][0]
        capability = manifest['manifest_json']['capabilities'][0]
        if not await self._is_workspace_app_enabled(db, workspace=workspace, app_id=manifest['app_id']):
            return self._capabilities_payload(workspace=workspace, agent=agent, manifest=manifest, tools=[])
        if not self._has_required_scopes(agent, tool['required_scopes']):
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
        agent: AgentTokenPayload,
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
        agent = self._require_agent(request)
        workspace = await self._resolve_workspace(db, agent=agent, requested_workspace=body.workspace)
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
                error_code='15013',
                context={'reason': 'app_not_enabled'},
            )
            return self._deny_payload(body.trace_id, '15013', 'app_not_enabled', audit_id=audit['id'])

        required_scopes = list(tool.get('required_scopes') or [])
        if not self._has_required_scopes(agent, required_scopes):
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

        input_payload = dict(body.input or {})
        if not self._valid_search_input(input_payload):
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

        if app_id != 'knowledge' or tool_id != 'knowledge.search':
            raise errors.NotFoundError(msg='AI-Native 工具不存在')

        result = await workbench_domain_service.search_current_knowledge(
            db,
            user_id=agent.owner_user_id,
            query=str(input_payload['query']),
            limit=int(input_payload.get('limit') or 50),
            dataset_id=input_payload.get('dataset_id'),
        )
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
        rows = (await db.execute(stmt.order_by(HasnAiNativeAppAudit.id.desc()))).scalars().all()
        return {'items': [self._audit_payload(row) for row in rows], 'total': len(rows)}

    def _require_agent(self, request) -> AgentTokenPayload:
        agent = getattr(request.state, 'agent', None)
        if agent is None:
            raise errors.TokenError(msg='Agent JWT 未认证')
        return agent

    async def _resolve_workspace(
        self,
        db,
        *,
        agent: AgentTokenPayload,
        requested_workspace: dict[str, Any] | None,
    ) -> dict[str, Any]:
        workspace = dict(
            requested_workspace
            or await workbench_domain_service.get_active_workspace(db, user_id=agent.owner_user_id)
        )
        kind = workspace.get('kind') or 'personal'
        if kind not in {'personal', 'enterprise'}:
            raise errors.RequestError(msg='invalid_workspace_kind')
        workspace['kind'] = kind
        if kind == 'personal':
            workspace['user_id'] = agent.owner_user_id
            workspace['enterprise_id'] = None
            workspace['workspace_key'] = f'personal:{agent.owner_user_id}'
            return workspace

        enterprise_id = workspace.get('enterprise_id')
        if enterprise_id is None:
            raise errors.RequestError(msg='enterprise workspace requires enterprise_id')
        membership = await workbench_domain_service._approved_membership(
            db, enterprise_id=int(enterprise_id), user_id=agent.owner_user_id
        )
        if membership is None:
            raise errors.ForbiddenError(msg='未加入该企业')
        workspace['user_id'] = None
        workspace['enterprise_id'] = int(enterprise_id)
        workspace['workspace_key'] = f'enterprise:{enterprise_id}'
        workspace['role'] = getattr(membership, 'role', 'member')
        return workspace

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

    def _has_required_scopes(self, agent: AgentTokenPayload, required_scopes: list[str]) -> bool:
        return set(required_scopes).issubset(set(agent.scopes))

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
            agent_hasn_id=agent.agent_hasn_id,
            owner_hasn_id=agent.owner_hasn_id,
            session_uuid=agent.session_uuid,
            method='tool_call',
            capability_id=capability.get('capability_id'),
            tool_id=tool.get('tool_id'),
            event_type='tool_call',
            required_scopes=list(tool.get('required_scopes') or []),
            agent_scopes_snapshot=list(agent.scopes),
            workspace_role=workspace.get('role') or ('owner' if workspace['kind'] == 'personal' else 'member'),
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
