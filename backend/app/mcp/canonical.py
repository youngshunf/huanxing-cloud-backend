"""Canonical MCP tool naming: source classification + name validation (P0).

Mirrors the Rust ``hasn-mcp::descriptor`` module so both servers enforce the
same naming rules. Pure modeling — no dispatch behavior change.

Fact sources: ``01-工具来源与命名.md`` (§2/§3/§5), ``02-Registry与承载模型.md``.
"""
from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass
from typing import Any, Literal

# Tool source classification (01 §1). Matches the Rust ``ToolSource`` enum.
ToolSource = Literal["platform", "app", "local", "external"]

# Second-level namespaces reserved by the platform (01 §3). App and External
# MCP tools must not use these; Platform and Local tools may.
RESERVED_NAMESPACES: frozenset[str] = frozenset(
    {
        "tool",
        "cloud",
        "local",
        "workspace",
        "agent",
        "audit",
        "confirmation",
        "auth",
        "system",
        "file",
        "memory",
    }
)

# The external MCP marker namespace (``hasn.ext.{server}.{tool}``).
EXTERNAL_MARKER = "ext"


class CanonicalNameError(ValueError):
    """Raised when a canonical tool name is malformed or violates naming rules."""


@dataclass(frozen=True)
class CanonicalName:
    """A validated canonical tool name."""

    full: str
    namespace: str
    action: str


def normalize_canonical_name(name: str) -> str:
    """Normalize a canonical name: trim surrounding whitespace."""
    return name.strip()


def _is_valid_segment(segment: str) -> bool:
    return bool(segment) and all(
        (char.isalnum() and char.isascii()) or char == "_" for char in segment
    )


def validate_canonical_name(name: str, source: ToolSource) -> CanonicalName:
    """Validate and parse a canonical tool name (01 §2/§3/§5).

    Rejects malformed names and reserved-namespace conflicts. ``namespace``
    keeps the ``hasn.`` prefix to match the discovery source index.

    Raises:
        CanonicalNameError: when the name is empty, malformed, mis-uses the
            ``hasn.ext.*`` marker, or — for App tools — uses a reserved
            namespace.
    """
    normalized = normalize_canonical_name(name)
    if not normalized:
        raise CanonicalNameError("canonical tool name is empty")

    segments = normalized.split(".")
    for segment in segments:
        if not _is_valid_segment(segment):
            raise CanonicalNameError(f"invalid segment in canonical tool name: {normalized}")

    if segments[0] != "hasn":
        raise CanonicalNameError(f"canonical tool name must start with 'hasn.': {normalized}")

    is_external = len(segments) > 1 and segments[1] == EXTERNAL_MARKER
    if is_external:
        if source != "external":
            raise CanonicalNameError(
                f"'hasn.ext.*' is reserved for external MCP tools: {normalized}"
            )
        if len(segments) < 4:
            raise CanonicalNameError(
                f"external tool must be 'hasn.ext.<server>.<tool>': {normalized}"
            )
        return CanonicalName(
            full=normalized,
            namespace=".".join(segments[:3]),
            action=".".join(segments[3:]),
        )

    if len(segments) < 3:
        raise CanonicalNameError(
            f"canonical tool name must be 'hasn.<namespace>.<action>': {normalized}"
        )

    namespace_segment = segments[1]
    if source == "app" and namespace_segment in RESERVED_NAMESPACES:
        raise CanonicalNameError(
            f"app tool may not use reserved namespace 'hasn.{namespace_segment}': {normalized}"
        )

    return CanonicalName(
        full=normalized,
        namespace=f"hasn.{namespace_segment}",
        action=".".join(segments[2:]),
    )


def schema_hash(schema: dict[str, Any]) -> str:
    """Compute a stable ``sha256:`` hash of a schema dict."""
    canonical = json.dumps(schema, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
