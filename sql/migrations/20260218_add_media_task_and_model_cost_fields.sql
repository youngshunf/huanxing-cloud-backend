-- Migration: 添加媒体生成任务表 + ModelConfig 计费字段
-- Date: 2026-02-18
-- Description: 创建 llm_media_task 表，为 llm_model_config 添加 cost_per_generation / cost_per_second 字段

-- =====================================================
-- 1. 创建 llm_media_task 表
-- =====================================================
CREATE TABLE IF NOT EXISTS llm_media_task (
    id            BIGSERIAL       PRIMARY KEY,
    task_id       VARCHAR(64)     NOT NULL,
    user_id       BIGINT          NOT NULL,
    api_key_id    BIGINT          NOT NULL,
    model_name    VARCHAR(128)    NOT NULL,
    provider_id   BIGINT          NOT NULL,
    media_type    VARCHAR(16)     NOT NULL,
    prompt        TEXT            NOT NULL,
    status        VARCHAR(16)     NOT NULL DEFAULT 'pending',
    progress      INTEGER         NOT NULL DEFAULT 0,
    params        JSONB           DEFAULT NULL,
    vendor_task_id VARCHAR(128)   DEFAULT NULL,
    vendor_urls   JSONB           DEFAULT NULL,
    oss_urls      JSONB           DEFAULT NULL,
    error_code    VARCHAR(32)     DEFAULT NULL,
    error_message TEXT            DEFAULT NULL,
    webhook_url   VARCHAR(512)    DEFAULT NULL,
    credits_cost          NUMERIC(10, 4) NOT NULL DEFAULT 0,
    credits_pre_deducted  NUMERIC(10, 4) NOT NULL DEFAULT 0,
    poll_count    INTEGER         NOT NULL DEFAULT 0,
    ip_address    VARCHAR(64)     DEFAULT NULL,
    completed_at  TIMESTAMPTZ     DEFAULT NULL,
    created_time  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_time  TIMESTAMPTZ     DEFAULT NULL
);

COMMENT ON TABLE  llm_media_task IS '媒体生成任务表';
COMMENT ON COLUMN llm_media_task.id IS '主键 ID';
COMMENT ON COLUMN llm_media_task.task_id IS '任务 ID (img-xxx / vid-xxx)';
COMMENT ON COLUMN llm_media_task.user_id IS '用户 ID';
COMMENT ON COLUMN llm_media_task.api_key_id IS 'API Key ID';
COMMENT ON COLUMN llm_media_task.model_name IS '模型名称';
COMMENT ON COLUMN llm_media_task.provider_id IS '供应商 ID';
COMMENT ON COLUMN llm_media_task.media_type IS '媒体类型 (image/video)';
COMMENT ON COLUMN llm_media_task.prompt IS '生成提示词';
COMMENT ON COLUMN llm_media_task.status IS '任务状态 (pending/processing/completed/failed)';
COMMENT ON COLUMN llm_media_task.progress IS '进度 0-100';
COMMENT ON COLUMN llm_media_task.params IS '请求参数 (JSONB)';
COMMENT ON COLUMN llm_media_task.vendor_task_id IS '厂商任务 ID';
COMMENT ON COLUMN llm_media_task.vendor_urls IS '厂商临时 URL (JSONB)';
COMMENT ON COLUMN llm_media_task.oss_urls IS 'OSS 永久 URL (JSONB)';
COMMENT ON COLUMN llm_media_task.error_code IS '错误码';
COMMENT ON COLUMN llm_media_task.error_message IS '错误信息';
COMMENT ON COLUMN llm_media_task.webhook_url IS 'Webhook 回调 URL';
COMMENT ON COLUMN llm_media_task.credits_cost IS '积分消耗';
COMMENT ON COLUMN llm_media_task.credits_pre_deducted IS '预扣积分';
COMMENT ON COLUMN llm_media_task.poll_count IS '轮询次数';
COMMENT ON COLUMN llm_media_task.ip_address IS 'IP 地址';
COMMENT ON COLUMN llm_media_task.completed_at IS '完成时间';
COMMENT ON COLUMN llm_media_task.created_time IS '创建时间';
COMMENT ON COLUMN llm_media_task.updated_time IS '更新时间';

-- 索引
CREATE UNIQUE INDEX IF NOT EXISTS ix_llm_media_task_task_id       ON llm_media_task (task_id);
CREATE INDEX IF NOT EXISTS ix_llm_media_task_user_id              ON llm_media_task (user_id);
CREATE INDEX IF NOT EXISTS ix_llm_media_task_api_key_id           ON llm_media_task (api_key_id);
CREATE INDEX IF NOT EXISTS ix_llm_media_task_model_name           ON llm_media_task (model_name);
CREATE INDEX IF NOT EXISTS ix_llm_media_task_provider_id          ON llm_media_task (provider_id);
CREATE INDEX IF NOT EXISTS ix_llm_media_task_media_type           ON llm_media_task (media_type);
CREATE INDEX IF NOT EXISTS ix_llm_media_task_status               ON llm_media_task (status);
CREATE INDEX IF NOT EXISTS ix_llm_media_task_vendor_task_id       ON llm_media_task (vendor_task_id);

-- =====================================================
-- 2. llm_model_config 新增媒体生成计费字段
-- =====================================================
ALTER TABLE llm_model_config ADD COLUMN IF NOT EXISTS cost_per_generation NUMERIC(10, 4) DEFAULT NULL;
COMMENT ON COLUMN llm_model_config.cost_per_generation IS '每次生成费用（图像用）';

ALTER TABLE llm_model_config ADD COLUMN IF NOT EXISTS cost_per_second NUMERIC(10, 4) DEFAULT NULL;
COMMENT ON COLUMN llm_model_config.cost_per_second IS '每秒费用（视频按时长用）';

-- =====================================================
-- 回滚脚本 (如需回滚，执行以下语句):
-- =====================================================
-- ALTER TABLE llm_model_config DROP COLUMN IF EXISTS cost_per_generation;
-- ALTER TABLE llm_model_config DROP COLUMN IF EXISTS cost_per_second;
-- DROP TABLE IF EXISTS llm_media_task;
