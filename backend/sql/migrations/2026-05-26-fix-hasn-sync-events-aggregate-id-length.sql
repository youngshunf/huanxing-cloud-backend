-- =====================================================
-- 修复 hasn_sync_events.aggregate_id 字段长度
-- 创建时间: 2026-05-26
-- 说明: aggregate_id 从 varchar(80) 扩展到 varchar(200)
-- =====================================================

-- 修改字段长度
ALTER TABLE "public"."hasn_sync_events"
ALTER COLUMN "aggregate_id" TYPE varchar(200);

-- 验证修改
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'hasn_sync_events'
AND column_name = 'aggregate_id';
