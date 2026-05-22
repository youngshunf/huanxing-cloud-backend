-- 2026-05-23: 会话分层云端投影表
-- 参考：docs/hasn-node设计文档/01-核心架构/09-会话分层与运行时会话路由设计.md
--
-- 云端只保存投影字段，不保存 runtime_sessions 等本地私密数据
-- 本地 SQLite 是完整事实源，云端是跨设备同步的投影
--
-- 注意：
-- 1. 云端使用 PostgreSQL，本地使用 SQLite
-- 2. 云端时间字段使用 timestamptz，本地使用 BIGINT
-- 3. 云端 hasn_conversations 主键是 id (UUID)，本地是 conversation_id (TEXT)

-- 1. 为 hasn_conversations 添加 session 指针字段
ALTER TABLE hasn_conversations
ADD COLUMN active_session_id VARCHAR(26),
ADD COLUMN last_session_id VARCHAR(26);

COMMENT ON COLUMN hasn_conversations.active_session_id IS '当前活跃的 session ID';
COMMENT ON COLUMN hasn_conversations.last_session_id IS '最后一个 session ID，用于恢复';

-- 2. 创建 hasn_sessions 投影表（只保存云端需要同步的字段）
CREATE TABLE hasn_sessions (
    session_id VARCHAR(26) PRIMARY KEY,
    conversation_id UUID,
    owner_id VARCHAR(40) NOT NULL,
    hasn_id VARCHAR(100) NOT NULL,
    session_kind VARCHAR(50) NOT NULL,
    session_scope VARCHAR(50) NOT NULL,
    session_status VARCHAR(50) NOT NULL DEFAULT 'active',
    parent_session_id VARCHAR(26),
    continuation_from_session_id VARCHAR(26),
    origin_type VARCHAR(50) NOT NULL,
    origin_ref VARCHAR(255),
    title VARCHAR(500),
    summary_checkpoint_json JSONB NOT NULL DEFAULT '{}',
    active_binding_id VARCHAR(26),
    last_message_id BIGINT,
    last_message_at TIMESTAMPTZ(6),
    created_time TIMESTAMPTZ(6) NOT NULL DEFAULT now(),
    updated_time TIMESTAMPTZ(6),
    closed_at TIMESTAMPTZ(6),
    FOREIGN KEY (conversation_id) REFERENCES hasn_conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_hasn_sessions_conversation
    ON hasn_sessions(conversation_id, created_time DESC);

CREATE INDEX idx_hasn_sessions_owner_hasn
    ON hasn_sessions(owner_id, hasn_id, session_status, last_message_at DESC);

CREATE INDEX idx_hasn_sessions_parent
    ON hasn_sessions(parent_session_id);

COMMENT ON TABLE hasn_sessions IS '会话分层投影表（云端同步）';
COMMENT ON COLUMN hasn_sessions.session_id IS '会话 ID';
COMMENT ON COLUMN hasn_sessions.conversation_id IS '所属对话 ID（可空，task/temporary/external 默认为空）';
COMMENT ON COLUMN hasn_sessions.owner_id IS '所有者 ID';
COMMENT ON COLUMN hasn_sessions.hasn_id IS 'HASN ID';
COMMENT ON COLUMN hasn_sessions.session_kind IS '会话类型 (interactive:交互/task:任务/temporary:临时/external:外部/system:系统)';
COMMENT ON COLUMN hasn_sessions.session_scope IS '同步范围 (conversation_visible:完整同步/summary_only:仅摘要/local_only:本地)';
COMMENT ON COLUMN hasn_sessions.session_status IS '会话状态 (active:活跃/closed:已关闭)';
COMMENT ON COLUMN hasn_sessions.parent_session_id IS '父会话 ID（分叉来源）';
COMMENT ON COLUMN hasn_sessions.continuation_from_session_id IS '延续自哪个会话（Runtime 切换）';
COMMENT ON COLUMN hasn_sessions.origin_type IS '创建来源 (ui:用户界面/task_run:任务/external_app:外部应用/system:系统)';
COMMENT ON COLUMN hasn_sessions.origin_ref IS '来源引用（如 task_run_id）';
COMMENT ON COLUMN hasn_sessions.title IS '会话标题';
COMMENT ON COLUMN hasn_sessions.summary_checkpoint_json IS '摘要检查点（用于跨设备恢复）';
COMMENT ON COLUMN hasn_sessions.active_binding_id IS '当前活跃的 binding ID';
COMMENT ON COLUMN hasn_sessions.last_message_id IS '最后一条消息 ID';
COMMENT ON COLUMN hasn_sessions.last_message_at IS '最后消息时间戳';

-- 3. 创建 hasn_session_events 投影表（只同步允许出端的摘要事件）
CREATE TABLE hasn_session_events (
    session_event_id VARCHAR(26) PRIMARY KEY,
    session_id VARCHAR(26) NOT NULL,
    owner_id VARCHAR(40) NOT NULL,
    hasn_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_seq BIGINT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}',
    redaction_level VARCHAR(50) NOT NULL DEFAULT 'internal',
    created_time TIMESTAMPTZ(6) NOT NULL DEFAULT now(),
    FOREIGN KEY (session_id) REFERENCES hasn_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_hasn_session_events_session_seq
    ON hasn_session_events(session_id, event_seq);

CREATE INDEX idx_hasn_session_events_type
    ON hasn_session_events(event_type, created_time DESC);

COMMENT ON TABLE hasn_session_events IS '会话事件投影表（只同步 summary/public 级别事件）';
COMMENT ON COLUMN hasn_session_events.session_event_id IS '事件 ID';
COMMENT ON COLUMN hasn_session_events.session_id IS '所属会话 ID';
COMMENT ON COLUMN hasn_session_events.event_type IS '事件类型 (task_started/runtime_chunk/tool_call/tool_result/checkpoint_written/task_result/external_result)';
COMMENT ON COLUMN hasn_session_events.event_seq IS '事件序号（会话内单调递增）';
COMMENT ON COLUMN hasn_session_events.payload_json IS '事件载荷';
COMMENT ON COLUMN hasn_session_events.redaction_level IS '脱敏级别 (internal:内部/summary:摘要/public:公开)';

-- 4. 创建 hasn_session_artifacts 投影表（只同步元数据和摘要）
CREATE TABLE hasn_session_artifacts (
    artifact_id VARCHAR(26) PRIMARY KEY,
    session_id VARCHAR(26) NOT NULL,
    owner_id VARCHAR(40) NOT NULL,
    hasn_id VARCHAR(100) NOT NULL,
    artifact_kind VARCHAR(50) NOT NULL,
    artifact_ref VARCHAR(500) NOT NULL,
    summary_json JSONB NOT NULL DEFAULT '{}',
    sync_policy VARCHAR(50) NOT NULL DEFAULT 'summary_only',
    created_time TIMESTAMPTZ(6) NOT NULL DEFAULT now(),
    updated_time TIMESTAMPTZ(6),
    FOREIGN KEY (session_id) REFERENCES hasn_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_hasn_session_artifacts_session
    ON hasn_session_artifacts(session_id, created_time DESC);

CREATE INDEX idx_hasn_session_artifacts_kind
    ON hasn_session_artifacts(artifact_kind, created_time DESC);

COMMENT ON TABLE hasn_session_artifacts IS '会话产物投影表（只同步元数据）';
COMMENT ON COLUMN hasn_session_artifacts.artifact_id IS '产物 ID';
COMMENT ON COLUMN hasn_session_artifacts.session_id IS '所属会话 ID';
COMMENT ON COLUMN hasn_session_artifacts.artifact_kind IS '产物类型 (file:文件/tool_output:工具输出/task_result:任务结果)';
COMMENT ON COLUMN hasn_session_artifacts.artifact_ref IS '产物引用（URI）';
COMMENT ON COLUMN hasn_session_artifacts.summary_json IS '产物摘要';
COMMENT ON COLUMN hasn_session_artifacts.sync_policy IS '同步策略 (summary_only:仅摘要/local_only:不同步)';

-- 5. 为 hasn_messages 添加 session_id 和 session_seq 字段
ALTER TABLE hasn_messages
ADD COLUMN session_id VARCHAR(26),
ADD COLUMN session_seq BIGINT;

COMMENT ON COLUMN hasn_messages.session_id IS '所属会话 ID（逻辑连续性）';
COMMENT ON COLUMN hasn_messages.session_seq IS '会话内序号（单调递增）';

CREATE INDEX idx_hasn_messages_session
    ON hasn_messages(session_id, session_seq);

-- 注意：
-- 1. runtime_sessions 不同步到云端（本地私密数据）
-- 2. message_runtime_attribution 不同步到云端（审计归因保留在本地）
-- 3. 云端只保存 conversation_visible 和 summary_only 的数据
-- 4. local_only 的 session 不会同步到云端
-- 5. 云端使用 timestamptz 时间类型，本地使用 BIGINT Unix 时间戳
-- 6. 云端 conversation_id 是 UUID，本地是 TEXT（ULID）
