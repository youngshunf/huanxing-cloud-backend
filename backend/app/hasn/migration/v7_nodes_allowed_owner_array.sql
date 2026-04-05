-- v7: hasn_nodes.owner_hasn_id -> allowed_owner_hasn_ids (array/json)
-- 目标:
-- 1. 将单值 owner_hasn_id 替换为数组字段 allowed_owner_hasn_ids
-- 2. 为现有数据回填：
--    - 如果原 owner_hasn_id 有值 -> [owner_hasn_id]
--    - 否则 -> NULL（表示桌面端默认不限制）

BEGIN;

ALTER TABLE public.hasn_nodes
    ADD COLUMN IF NOT EXISTS allowed_owner_hasn_ids jsonb;

COMMENT ON COLUMN public.hasn_nodes.allowed_owner_hasn_ids
IS '允许绑定的 Owner 列表 JSON（NULL/空数组表示不限制，SDK 场景可指定白名单）';

UPDATE public.hasn_nodes
SET allowed_owner_hasn_ids = jsonb_build_array(owner_hasn_id)
WHERE allowed_owner_hasn_ids IS NULL
  AND owner_hasn_id IS NOT NULL
  AND owner_hasn_id <> '';

ALTER TABLE public.hasn_nodes
    DROP COLUMN IF EXISTS owner_hasn_id;

DROP INDEX IF EXISTS idx_hasn_nodes_owner_hasn_id;

COMMIT;
