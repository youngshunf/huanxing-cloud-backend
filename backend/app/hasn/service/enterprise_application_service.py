from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from backend.utils.timezone import timezone


@dataclass(frozen=True)
class InviteCodePolicy:
    max_uses: int | None
    used_count: int
    revoked: bool
    expires_at: datetime | str | None

    def validate(self, *, now: datetime | None = None) -> str | None:
        now = now or timezone.now()
        if self.revoked:
            return 'invite_code_revoked'
        expires_at = _coerce_datetime(self.expires_at)
        if expires_at is not None and expires_at <= now:
            return 'invite_code_expired'
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return 'invite_code_used_up'
        return None


class EnterpriseApplicationService:
    @staticmethod
    def decide_status_for_invite(auto_approve: bool) -> str:
        return 'approved' if auto_approve else 'pending'

    @staticmethod
    def validate_invite_code(
        *,
        max_uses: int | None,
        used_count: int,
        revoked: bool,
        expires_at: datetime | None,
        now: datetime | None = None,
    ) -> str | None:
        return InviteCodePolicy(
            max_uses=max_uses,
            used_count=used_count,
            revoked=revoked,
            expires_at=expires_at,
        ).validate(now=now)


enterprise_application_service = EnterpriseApplicationService()


def _coerce_datetime(value: Any) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, str):
        normalized = value.strip()
        if normalized == '':
            return None
        return datetime.fromisoformat(normalized)
    raise TypeError(f'unsupported datetime value: {type(value)!r}')
