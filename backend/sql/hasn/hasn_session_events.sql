-- hasn_session_events 表
CREATE TABLE hasn_session_events (
    session_event_id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    owner_id VARCHAR(64) NOT NULL,
    hasn_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_seq INTEGER NOT NULL,
    payload_json JSONB DEFAULT '{}',
    redaction_level VARCHAR(20) NOT NULL DEFAULT 'internal',
    created_time TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_redaction_level CHECK (
        redaction_level IN ('internal', 'summary', 'public')
    )
);

CREATE INDEX idx_hasn_session_events_session ON hasn_session_events(session_id, event_seq);
CREATE INDEX idx_hasn_session_events_type ON hasn_session_events(event_type);
CREATE INDEX idx_hasn_session_events_owner ON hasn_session_events(owner_id);
CREATE INDEX idx_hasn_session_events_hasn ON hasn_session_events(hasn_id);

COMMENT ON TABLE hasn_session_events IS 'Session 事件投影表（云端，只保存摘要事件）';
COMMENT ON COLUMN hasn_session_events.session_event_id IS '事件全局唯一 ID（ULID 格式）';
COMMENT ON COLUMN hasn_session_events.session_id IS '所属 Session ID';
COMMENT ON COLUMN hasn_session_events.owner_id IS '所属 Owner ID';
COMMENT ON COLUMN hasn_session_events.hasn_id IS '所属 Agent ID';
COMMENT ON COLUMN hasn_session_events.event_type IS '事件类型（如 tool_call、thinking、error 等）';
COMMENT ON COLUMN hasn_session_events.event_seq IS '事件序号（Session 内递增）';
COMMENT ON COLUMN hasn_session_events.payload_json IS '事件负载（JSON 格式）';
COMMENT ON COLUMN hasn_session_events.redaction_level IS '脱敏级别 (internal:内部:gray/summary:摘要:blue/public:公开:green)，只同步 summary 和 public';
COMMENT ON COLUMN hasn_session_events.created_time IS '创建时间';
