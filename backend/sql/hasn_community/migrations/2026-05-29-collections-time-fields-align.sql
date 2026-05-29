-- 对齐收藏夹时间字段命名规范（created_time/updated_time），匹配 ORM 模型与项目约定
-- doc-12 Phase D：hasn_collections / hasn_collection_items 历史 codegen 用了 create_time/update_time，
-- 与 backend ORM 模型（created_time/updated_time）不一致，导致收藏相关 ORM 查询无法运行。
-- 本迁移把 DB 列名改为规范名（幂等：仅当旧列存在时改）。

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_schema='public' AND table_name='hasn_collections' AND column_name='create_time') THEN
        ALTER TABLE "public"."hasn_collections" RENAME COLUMN "create_time" TO "created_time";
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_schema='public' AND table_name='hasn_collections' AND column_name='update_time') THEN
        ALTER TABLE "public"."hasn_collections" RENAME COLUMN "update_time" TO "updated_time";
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_schema='public' AND table_name='hasn_collection_items' AND column_name='create_time') THEN
        ALTER TABLE "public"."hasn_collection_items" RENAME COLUMN "create_time" TO "created_time";
    END IF;
END $$;
