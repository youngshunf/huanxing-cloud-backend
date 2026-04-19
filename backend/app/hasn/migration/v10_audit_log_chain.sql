-- HASN 审计因果链 v10.0 — DB 迁移
-- 版本: Phase 7 — hasn_audit_log 扩 prev_log_id / hash_chain / findings / severity
-- 日期: 2026-04-19
-- 描述: 对齐设计 05 §3.2 审计因果链 (sha256(prev_hash + canonical_json(details)))
--        actor_id 作链作用域；与 Rust Node 侧 owner_id 链独立 (后端无 node_id 列)
--
-- 执行: psql $DATABASE_URL -f v10_audit_log_chain.sql

BEGIN;

-- Step 1: 加 4 列 (hash_chain 用 NOT NULL DEFAULT '' 兼容旧行；Postgres 11+ 零表锁)
ALTER TABLE hasn_audit_log ADD COLUMN IF NOT EXISTS prev_log_id BIGINT REFERENCES hasn_audit_log(id);
ALTER TABLE hasn_audit_log ADD COLUMN IF NOT EXISTS hash_chain VARCHAR(64) NOT NULL DEFAULT '';
ALTER TABLE hasn_audit_log ADD COLUMN IF NOT EXISTS findings JSONB NOT NULL DEFAULT '[]'::jsonb;
ALTER TABLE hasn_audit_log ADD COLUMN IF NOT EXISTS severity VARCHAR(16);

-- Step 2: 索引 (加速按 actor_id 取最新一条 + 按因果链遍历)
CREATE INDEX IF NOT EXISTS idx_audit_actor_prev ON hasn_audit_log(actor_id, prev_log_id);
CREATE INDEX IF NOT EXISTS idx_audit_actor_id_desc ON hasn_audit_log(actor_id, id DESC);

-- Step 3: 字段注释
COMMENT ON COLUMN hasn_audit_log.prev_log_id IS '前驱 log id (同 actor_id 链作用域)';
COMMENT ON COLUMN hasn_audit_log.hash_chain  IS 'SHA-256(prev_hash || canonical_json(details))';
COMMENT ON COLUMN hasn_audit_log.findings    IS '脱敏发现列表 (本 phase 空占位)';
COMMENT ON COLUMN hasn_audit_log.severity    IS 'info/warning/error';

-- Step 4: 验证
DO $$
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_name = 'hasn_audit_log'
      AND column_name IN ('prev_log_id', 'hash_chain', 'findings', 'severity');
    IF col_count <> 4 THEN
        RAISE EXCEPTION '迁移验证失败: 期望 4 个新列，实际 %', col_count;
    END IF;
    RAISE NOTICE '✅ hasn_audit_log 因果链列已就绪';
END $$;

COMMIT;
