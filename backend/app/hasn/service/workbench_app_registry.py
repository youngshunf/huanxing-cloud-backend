from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True)
class WorkbenchApp:
    id: str
    name: str
    icon: str
    description: str
    scope: tuple[str, ...]
    entry_route: str
    install_policy: str
    requires_role: str | None = None
    health_check: Callable[[dict[str, Any]], dict[str, Any]] | None = None

    def to_manifest(self, *, workspace_kind: str | None = None) -> dict[str, Any]:
        data = {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'description': self.description,
            'scope': list(self.scope),
            'entry_route': self.entry_route,
            'install_policy': self.install_policy,
            'requires_role': self.requires_role,
        }
        if workspace_kind and self.health_check:
            data['health'] = self.health_check({'workspace_kind': workspace_kind})
        return data


class WorkbenchAppRegistry:
    def __init__(self) -> None:
        self._apps: dict[str, WorkbenchApp] = {}

    @classmethod
    def default(cls) -> WorkbenchAppRegistry:
        registry = cls()
        registry.register(
            WorkbenchApp(
                id='knowledge',
                name='知识库',
                icon='book-open',
                description='在当前工作空间管理知识库、搜索与审计。',
                scope=('personal', 'enterprise'),
                entry_route='/workbench/apps/knowledge',
                install_policy='auto',
            )
        )
        return registry

    def register(self, app: WorkbenchApp) -> None:
        self._apps[app.id] = app

    def get(self, app_id: str) -> WorkbenchApp:
        return self._apps[app_id]

    def list(self, workspace_kind: str | None = None) -> list[WorkbenchApp]:
        apps = list(self._apps.values())
        if workspace_kind:
            apps = [app for app in apps if workspace_kind in app.scope]
        return apps

    def auto_install_apps(self, workspace_kind: str) -> list[WorkbenchApp]:
        return [app for app in self.list(workspace_kind) if app.install_policy == 'auto']


workbench_app_registry = WorkbenchAppRegistry.default()
