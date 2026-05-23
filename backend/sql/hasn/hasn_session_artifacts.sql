-- hasn_session_artifacts 表
CREATE TABLE hasn_session_artifacts (
    artifact_id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    owner_id VARCHAR(64) NOT NULL,
    hasn_id VARCHAR(64) NOT NULL,
    artifact_kind VARCHAR(50) NOT NULL,
    artifact_ref VARCHAR(500) NOT NULL,
    summary_json JSONB DEFAULT '{}',
    sync_policy VARCHAR(20) NOT NULL DEFAULT 'summary_only',
    created_time TIMESTAMPTZ DEFAULT NOW(),
    updated_time TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_sync_policy CHECK (
        sync_policy IN ('summary_only', 'full', 'none')
    )
);

CREATE INDEX idx_hasn_session_artifacts_session ON hasn_session_artifacts(session_id);
CREATE INDEX idx_hasn_session_artifacts_kind ON hasn_session_artifacts(artifact_kind);
CREATE INDEX idx_hasn_session_artifacts_owner ON hasn_session_artifacts(owner_id);
CREATE INDEX idx_hasn_session_artifacts_hasn ON hasn_session_artifacts(hasn_id);

COMMENT ON TABLE hasn_session_artifacts IS 'Session 产物投影表（云端，只保存元数据）';
COMMENT ON COLUMN hasn_session_artifacts.artifact_id IS '产物全局唯一 ID（ULID 格式）';
COMMENT ON COLUMN hasn_session_artifacts.session_id IS '所属 Session ID';
COMMENT ON COLUMN hasn_session_artifacts.owner_id IS '所属 Owner ID';
COMMENT ON COLUMN hasn_session_artifacts.hasn_id IS '所属 Agent ID';
COMMENT ON COLUMN hasn_session_artifacts.artifact_kind IS '产物类型（如 file、image、code、report 等）';
COMMENT ON COLUMN hasn_session_artifacts.artifact_ref IS '产物引用，指向对象存储或资产服务';
COMMENT ON COLUMN hasn_session_artifacts.summary_json IS '产物摘要（JSON 格式）';
COMMENT ON COLUMN hasn_session_artifacts.sync_policy IS '同步策略 (summary_only:仅摘要:blue/full:完整:green/none:不同步:gray)';
COMMENT ON COLUMN hasn_session_artifacts.created_time IS '创建时间';
COMMENT ON COLUMN hasn_session_artifacts.updated_time IS '更新时间';
