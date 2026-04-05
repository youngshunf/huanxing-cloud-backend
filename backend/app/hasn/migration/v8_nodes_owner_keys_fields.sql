-- v8: 补齐 hasn_nodes / hasn_owner_api_keys 字段
-- 目标:
-- 1. hasn_nodes 增加 user_id / allowed_owner_hasn_ids / device_* / app_version
-- 2. hasn_owner_api_keys 增加 user_id
-- 3. 为现有数据做基础回填

BEGIN;

-- ============================================================
-- 1) hasn_nodes
-- ============================================================

ALTER TABLE public.hasn_nodes
    ADD COLUMN IF NOT EXISTS user_id bigint,
    ADD COLUMN IF NOT EXISTS allowed_owner_hasn_ids jsonb,
    ADD COLUMN IF NOT EXISTS device_fingerprint varchar(128),
    ADD COLUMN IF NOT EXISTS device_platform varchar(32),
    ADD COLUMN IF NOT EXISTS app_version varchar(32);

COMMENT ON COLUMN public.hasn_nodes.user_id
IS '平台用户 ID（桌面端/唤星账号场景）';

COMMENT ON COLUMN public.hasn_nodes.allowed_owner_hasn_ids
IS '允许绑定的 Owner 列表 JSON（NULL/空数组表示不限制，SDK 场景可指定白名单）';

COMMENT ON COLUMN public.hasn_nodes.device_fingerprint
IS '设备指纹（用于幂等创建和识别同一设备）';

COMMENT ON COLUMN public.hasn_nodes.device_platform
IS '设备平台 (macos:macOS:blue/windows:Windows:cyan/linux:Linux:green/ios:iOS:purple/android:Android:orange/web:Web:gray/sdk:SDK:yellow/server:Server:red)';

COMMENT ON COLUMN public.hasn_nodes.app_version
IS '接入端应用版本';

CREATE INDEX IF NOT EXISTS idx_hasn_nodes_user_id
    ON public.hasn_nodes(user_id);

CREATE INDEX IF NOT EXISTS idx_hasn_nodes_device_fingerprint
    ON public.hasn_nodes(device_fingerprint);

-- 如果还存在旧字段 owner_hasn_id，则迁移到 allowed_owner_hasn_ids
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'hasn_nodes'
          AND column_name = 'owner_hasn_id'
    ) THEN
        EXECUTE $SQL$
            UPDATE public.hasn_nodes
            SET allowed_owner_hasn_ids = jsonb_build_array(owner_hasn_id)
            WHERE allowed_owner_hasn_ids IS NULL
              AND owner_hasn_id IS NOT NULL
              AND owner_hasn_id <> ''
        $SQL$;

        EXECUTE 'ALTER TABLE public.hasn_nodes DROP COLUMN owner_hasn_id';
        EXECUTE 'DROP INDEX IF EXISTS idx_hasn_nodes_owner_hasn_id';
    END IF;
END $$;

-- user_id / device 字段的基础回填
UPDATE public.hasn_nodes
SET
    user_id = COALESCE(
        user_id,
        (
            SELECT hh.user_id
            FROM public.hasn_humans hh
            WHERE hh.hasn_id = public.hasn_nodes.created_by_owner_id
            LIMIT 1
        )
    ),
    device_fingerprint = COALESCE(device_fingerprint, node_info ->> 'device_fingerprint'),
    device_platform = COALESCE(device_platform, node_info ->> 'device_platform', node_info ->> 'platform'),
    app_version = COALESCE(app_version, node_info ->> 'app_version');

-- ============================================================
-- 2) hasn_owner_api_keys
-- ============================================================

ALTER TABLE public.hasn_owner_api_keys
    ADD COLUMN IF NOT EXISTS user_id bigint;

COMMENT ON COLUMN public.hasn_owner_api_keys.user_id
IS '平台用户 ID（桌面端/唤星账号场景）';

CREATE INDEX IF NOT EXISTS idx_hasn_owner_api_keys_user
    ON public.hasn_owner_api_keys(user_id);

UPDATE public.hasn_owner_api_keys hok
SET user_id = COALESCE(
    hok.user_id,
    (
        SELECT hh.user_id
        FROM public.hasn_humans hh
        WHERE hh.hasn_id = hok.owner_id
        LIMIT 1
    )
);

COMMIT;
