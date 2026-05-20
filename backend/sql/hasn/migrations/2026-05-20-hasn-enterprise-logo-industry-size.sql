-- =====================================================
-- 2026-05-20 HASN 企业实体字段补全
-- 1. 企业实体增加 logo / industry / company_size
-- 2. 保持 slug 由云端生成，但历史数据继续兼容
-- =====================================================

ALTER TABLE hasn_enterprise
    ADD COLUMN IF NOT EXISTS logo VARCHAR(512),
    ADD COLUMN IF NOT EXISTS industry VARCHAR(64),
    ADD COLUMN IF NOT EXISTS company_size VARCHAR(32);

COMMENT ON COLUMN hasn_enterprise.logo IS '企业 Logo';
COMMENT ON COLUMN hasn_enterprise.industry IS '所属行业';
COMMENT ON COLUMN hasn_enterprise.company_size IS '企业规模';
