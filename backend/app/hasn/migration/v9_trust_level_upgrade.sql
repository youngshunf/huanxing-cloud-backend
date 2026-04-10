-- HASN 信任等级升级 v9.0 — DB 迁移
-- 版本: Phase 2 — 六级信任体系升位
-- 日期: 2026-04-10
-- 描述: 将 hasn_contacts.trust_level 从 0-4 体系升级至 0-5 体系
--   旧: 0=blocked, 1=stranger, 2=normal, 3=trusted, 4=owner
--   新: 0=blocked, 1=stranger, 2=normal, 3=friend, 4=trusted, 5=owner
--
-- 执行: psql $DATABASE_URL -f v9_trust_level_upgrade.sql

BEGIN;

-- Step 1: 旧 owner(4) → 新 所有者(5)
-- 必须先升 4→5，再升 3→4，避免数值覆盖
UPDATE hasn_contacts
SET trust_level = 5
WHERE trust_level = 4;

-- Step 2: 旧 trusted(3) → 新 密友(4)
UPDATE hasn_contacts
SET trust_level = 4
WHERE trust_level = 3;

-- Step 3: 更新字段注释（不影响运行，仅文档）
COMMENT ON COLUMN hasn_contacts.trust_level IS
  '信任等级 (0:已拉黑:red/1:陌生人:gray/2:普通联系人:blue/3:朋友:green/4:密友:orange/5:所有者:purple)';

-- Step 4: 添加 CHECK 约束（防止写入越界值）
-- 先删旧约束(如有)，再添新约束
ALTER TABLE hasn_contacts DROP CONSTRAINT IF EXISTS chk_trust_level_range;
ALTER TABLE hasn_contacts
  ADD CONSTRAINT chk_trust_level_range
  CHECK (trust_level >= 0 AND trust_level <= 5);

-- Step 5: 验证迁移结果
DO $$
DECLARE
  invalid_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO invalid_count
  FROM hasn_contacts
  WHERE trust_level NOT BETWEEN 0 AND 5;

  IF invalid_count > 0 THEN
    RAISE EXCEPTION '迁移验证失败: % 条记录的 trust_level 超出 0-5 范围', invalid_count;
  END IF;

  RAISE NOTICE '✅ 迁移验证通过，所有 trust_level 值均在 0-5 范围内';
END $$;

COMMIT;
