from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class RAGFlowResponse:
    status_code: int
    headers: dict[str, str]
    body: dict[str, Any]


class RAGFlowClient:
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> RAGFlowResponse:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.request(method, path, params=params, json=json, headers=headers)
            response.raise_for_status()
            body = response.json() if response.content else {}
            return RAGFlowResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=body,
            )

    async def get(
        self, path: str, *, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        return (await self.request('GET', path, params=params, headers=headers)).body

    async def post(
        self, path: str, *, json: dict[str, Any] | None = None, headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        return (await self.request('POST', path, json=json, headers=headers)).body

    async def patch(
        self, path: str, *, json: dict[str, Any] | None = None, headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        return (await self.request('PATCH', path, json=json, headers=headers)).body

    async def delete(self, path: str, *, headers: dict[str, str] | None = None) -> dict[str, Any]:
        return (await self.request('DELETE', path, headers=headers)).body
