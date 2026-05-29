"""Canonical tool-name validation + source classification tests (P0).

Mirrors the Rust ``hasn-mcp::descriptor`` unit tests so both servers enforce
identical naming rules.
"""
from __future__ import annotations

import pytest

from backend.app.mcp.canonical import CanonicalNameError, validate_canonical_name
from backend.app.mcp.tool_directory import ToolDirectoryService
from backend.app.mcp.tools.app_tools import AppTool
from backend.app.mcp.tools.registry import ToolRegistry
from backend.app.mcp.tools.tool_search import ToolSearchTool


class TestCanonicalValidation:
    def test_parses_platform_name(self) -> None:
        parsed = validate_canonical_name("hasn.tool.search", "platform")
        assert parsed.namespace == "hasn.tool"
        assert parsed.action == "search"

    def test_parses_app_multi_segment_action(self) -> None:
        parsed = validate_canonical_name("hasn.crm.lead.create", "app")
        assert parsed.namespace == "hasn.crm"
        assert parsed.action == "lead.create"

    def test_parses_external_name(self) -> None:
        parsed = validate_canonical_name("hasn.ext.gmail.draft_email", "external")
        assert parsed.namespace == "hasn.ext.gmail"
        assert parsed.action == "draft_email"

    def test_rejects_app_in_reserved_namespace(self) -> None:
        with pytest.raises(CanonicalNameError):
            validate_canonical_name("hasn.memory.search", "app")

    def test_allows_local_in_reserved_namespace(self) -> None:
        parsed = validate_canonical_name("hasn.memory.search", "local")
        assert parsed.namespace == "hasn.memory"

    def test_rejects_ext_marker_for_non_external(self) -> None:
        with pytest.raises(CanonicalNameError):
            validate_canonical_name("hasn.ext.gmail.draft_email", "app")

    def test_rejects_non_hasn_prefix(self) -> None:
        with pytest.raises(CanonicalNameError):
            validate_canonical_name("workbench.crm.lead.create", "app")

    def test_rejects_too_short(self) -> None:
        with pytest.raises(CanonicalNameError):
            validate_canonical_name("hasn.search", "platform")

    def test_rejects_empty_and_malformed_segments(self) -> None:
        with pytest.raises(CanonicalNameError):
            validate_canonical_name("hasn..search", "platform")
        with pytest.raises(CanonicalNameError):
            validate_canonical_name("hasn.tool.sea rch", "platform")

    def test_normalizes_surrounding_whitespace(self) -> None:
        parsed = validate_canonical_name("  hasn.tool.search  ", "platform")
        assert parsed.full == "hasn.tool.search"


class TestSourceClassificationAndDescriptor:
    def test_app_tool_source_and_descriptor(self) -> None:
        tool = AppTool(
            installation_id="appi_knowledge",
            app_id="knowledge",
            app_namespace="knowledge",
            tool_id="knowledge.search",
            tool_name="search",
            action="search",
            tool_description="Search workspace knowledge",
            tool_input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
            tool_output_schema={"type": "object"},
            tool_required_scopes=["knowledge.read"],
            risk_level="low",
        )
        assert tool.source == "app"

        descriptor = tool.descriptor()
        assert descriptor["canonical_name"] == "hasn.knowledge.search"
        assert descriptor["source"] == "app"
        assert descriptor["namespace"] == "hasn.knowledge"
        assert descriptor["action"] == "search"
        assert descriptor["required_scopes"] == ["knowledge.read"]
        assert descriptor["risk_level"] == "low"
        assert descriptor["execution_location"] == "cloud"
        assert descriptor["input_schema_hash"].startswith("sha256:")
        assert descriptor["output_schema_hash"].startswith("sha256:")

    def test_app_tool_rejects_reserved_namespace_at_construction(self) -> None:
        with pytest.raises(CanonicalNameError):
            AppTool(
                installation_id="appi_bad",
                app_id="bad",
                app_namespace="memory",  # reserved namespace
                tool_id="bad.search",
                tool_name="search",
                action="search",
                tool_description="bad tool",
                tool_input_schema={"type": "object"},
                tool_required_scopes=[],
            )

    def test_tool_search_is_platform_source(self) -> None:
        registry = ToolRegistry()
        directory = ToolDirectoryService(registry)
        search = ToolSearchTool(directory)

        assert search.source == "platform"
        descriptor = search.descriptor()
        assert descriptor["source"] == "platform"
        assert descriptor["namespace"] == "hasn.tool"
        assert descriptor["execution_location"] == "cloud"
