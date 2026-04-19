"""Phase 7: Permission Engine —— 中央四态判决入口 (A 路线，设计 01 §3)。

evaluate(db, sender, receiver, envelope) → DecisionResult
- 优先调 iron_laws.check_iron_laws；命中即返回
- iron_laws None → 灰度委托 route_guard.check_permission (仅 diff log，不阻断；灰度期 1 周后评估退役)
- 矩阵层默认 ALLOW (细粒度矩阵留给 spawner 工具层 phase)
- 任何路径都 _audit_safe(...) 写一条 permission_decision audit (失败仅 log.warning)
- Fail-closed 在 evaluate 顶层 try/except 内：内部异常 → DENY error_code=2099 (D-03)

下游契约：返回的 DecisionResult.decision 字面量必须是 'allow' / 'deny' /
'confirm_required' / 'scope_limited'，与 07-01 hasn_core::PermissionDecision
serde rename_all='snake_case' 字节对齐 (router 投递 envelope 时直接写入)。
"""
from __future__ import annotations

from typing import Any

from backend.app.hasn.constants import ALLOW, DENY
from backend.app.hasn.service.hasn_audit_log_service import hasn_audit_log_service
from backend.app.hasn.service.iron_laws import DecisionResult, check_iron_laws
from backend.app.hasn.service.route_guard import route_guard
from backend.common.log import log


class PermissionEngine:
    """中央四态判决器 (单例，模块级 permission_engine 暴露)。"""

    async def evaluate(
        self,
        db: Any,  # AsyncSession
        *,
        sender: dict[str, Any],
        receiver: dict[str, Any],
        envelope: dict[str, Any],
    ) -> DecisionResult:
        """中央判决入口。Fail-closed on internal exception (D-03)。"""
        try:
            # 1. 七铁律优先
            iron = await check_iron_laws(db, sender, receiver, envelope)
            if iron is not None:
                await self._audit_safe(db, sender, receiver, iron)
                return iron

            # 2. 灰度委托 route_guard 做 diff log (不阻断；灰度期 1 周)
            try:
                legacy_ok = await route_guard.check_permission(
                    db,
                    sender.get('hasn_id', ''),
                    receiver.get('hasn_id', ''),
                    envelope.get('relation_type', 'social'),
                )
                if not legacy_ok:
                    log.warning(
                        f'[perm_engine] matrix allow 但 route_guard deny: '
                        f'{sender.get("hasn_id")} → {receiver.get("hasn_id")}'
                    )
            except Exception as exc:
                log.warning(f'[perm_engine] route_guard 灰度调用失败, 忽略: {exc}')

            # 3. 矩阵默认 ALLOW (细粒度矩阵留给 spawner 工具层 phase)
            result = DecisionResult(
                decision=ALLOW,
                reason='matrix passed',
                matched_rule='matrix',
            )
            await self._audit_safe(db, sender, receiver, result)
            return result

        except Exception as exc:
            log.exception(
                f'[perm_engine] evaluate 内部异常, Fail-closed DENY: {exc}'
            )
            fail = DecisionResult(
                decision=DENY,
                reason='internal error, fail-closed',
                matched_rule='exception',
                error_code=2099,
            )
            await self._audit_safe(db, sender, receiver, fail, severity='warning')
            return fail

    async def _audit_safe(
        self,
        db: Any,
        sender: dict[str, Any],
        receiver: dict[str, Any],
        result: DecisionResult,
        severity: str | None = None,
    ) -> None:
        """审计写入。失败仅 log.warning，不 raise (业务可用性优先 / L8)。"""
        try:
            await hasn_audit_log_service.append(
                db=db,
                actor_id=sender.get('hasn_id') or 'central',
                actor_type=sender.get('entity_type', 'system'),
                action='permission_decision',
                target_id=receiver.get('hasn_id'),
                target_type=receiver.get('entity_type', 'agent'),
                details={
                    'decision': result.decision,
                    'reason': result.reason,
                    'matched_rule': result.matched_rule,
                    'allowed_fields': result.allowed_fields,
                    'from': sender.get('hasn_id'),
                    'to': receiver.get('hasn_id'),
                },
                severity=severity or (
                    'warning' if result.decision == DENY else None
                ),
            )
        except Exception as exc:
            log.warning(f'[perm_engine] audit append 失败 (不阻断): {exc}')


# 模块级单例 (与 route_guard / hasn_audit_log_service 保持同风格)
permission_engine: PermissionEngine = PermissionEngine()
