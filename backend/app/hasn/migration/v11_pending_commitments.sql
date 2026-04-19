-- HASN 承诺暂存 v11.0 — DB 迁移
-- 版本: Phase 7 — hasn_pending_commitments 新建
-- 日期: 2026-04-19
-- 描述: confirm_required 判决下中央暂存消息体，供桌面端通过 /hasn-events SSE 领取后确认
--        默认 24h TTL；过期由后台 prune job 清理 (本 phase 不实现 prune 调度)
--
-- 执行: psql $DATABASE_URL -f v11_pending_commitments.sql

BEGIN;

CREATE TABLE IF NOT EXISTS hasn_pending_commitments (
    id           VARCHAR(64) PRIMARY KEY,
    action_type  VARCHAR(64)  NOT NULL,
    sender_id    VARCHAR(64)  NOT NULL,
    receiver_id  VARCHAR(64)  NOT NULL,
    payload_json JSONB        NOT NULL,
    reason       VARCHAR(200),
    expires_at   TIMESTAMPTZ  NOT NULL,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pending_receiver ON hasn_pending_commitments(receiver_id, expires_at);
CREATE INDEX IF NOT EXISTS idx_pending_expires  ON hasn_pending_commitments(expires_at);

COMMENT ON TABLE hasn_pending_commitments IS 'Phase 7 confirm_required 暂存；24h TTL by default';
COMMENT ON COLUMN hasn_pending_commitments.action_type  IS '触发暂存的动作类型 (e.g. message_deliver / make_appointment)';
COMMENT ON COLUMN hasn_pending_commitments.payload_json IS '原始消息或动作 payload (canonical JSON)';
COMMENT ON COLUMN hasn_pending_commitments.reason       IS '触发 confirm 的理由 (来自 iron_law / matrix decision)';

-- 验证
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'hasn_pending_commitments'
    ) THEN
        RAISE EXCEPTION '迁移验证失败: hasn_pending_commitments 表未创建';
    END IF;
    RAISE NOTICE '✅ hasn_pending_commitments 表已就绪';
END $$;

COMMIT;
