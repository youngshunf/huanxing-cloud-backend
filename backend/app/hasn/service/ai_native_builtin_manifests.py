from __future__ import annotations

KNOWLEDGE_AI_NATIVE_MANIFEST = {
    'app_id': 'knowledge',
    'version': '1.0.0',
    'workspace_scope': ['personal', 'enterprise'],
    'collaboration_mode': 'workspace_shared',
    'capabilities': [
        {
            'capability_id': 'knowledge.search.capability',
            'name': '检索知识库',
            'description': '检索当前工作空间的知识库资料',
            'tool_id': 'knowledge.search',
            'mcp_name': 'hasn.knowledge.search',
            'required_scopes': ['knowledge.read'],
            'workspace_roles': ['owner', 'admin', 'member'],
            'input_schema': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string', 'minLength': 1},
                    'limit': {'type': 'integer', 'minimum': 1, 'maximum': 50},
                    'dataset_id': {'type': ['string', 'null']},
                },
                'required': ['query'],
                'additionalProperties': False,
            },
            'output_schema': {'type': 'object'},
            'risk_level': 'low',
            'human_confirmation': {'required': False},
            'result_writeback': ['audit', 'agent_message'],
            'discovery': {
                'exposure': 'on_demand',
                'summary': '检索当前工作空间的知识库资料',
                'tags': ['knowledge', 'search', 'read'],
                'schema_visibility': 'authorized_agents',
                'default_page_rank': 10,
            },
        }
    ],
    'tools': [
        {
            'tool_id': 'knowledge.search',
            'mcp_name': 'hasn.knowledge.search',
            'transport': 'gateway_internal',
            'handler': 'knowledge.search',
            'required_scopes': ['knowledge.read'],
            'risk_level': 'low',
            'idempotent': True,
        }
    ],
    'events': [],
    'reverse_invoke': {'supported': False},
    'audit': {
        'fields': [
            'trace_id',
            'workspace',
            'app_id',
            'agent_hasn_id',
            'owner_hasn_id',
            'session_uuid',
            'tool_id',
            'required_scopes',
            'decision',
        ]
    },
}
