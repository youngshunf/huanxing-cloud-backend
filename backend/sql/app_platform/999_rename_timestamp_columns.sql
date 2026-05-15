-- 重命名所有表的时间戳列：created_at -> created_time, updated_at -> updated_time

-- 权限系统表
ALTER TABLE app_permission_grants RENAME COLUMN created_at TO created_time;
ALTER TABLE app_permission_grants RENAME COLUMN updated_at TO updated_time;

ALTER TABLE app_dynamic_permission_requests RENAME COLUMN created_at TO created_time;
ALTER TABLE app_dynamic_permission_requests RENAME COLUMN updated_at TO updated_time;

ALTER TABLE app_scopes RENAME COLUMN created_at TO created_time;
ALTER TABLE app_scopes RENAME COLUMN updated_at TO updated_time;

-- 应用核心表
ALTER TABLE app_developers RENAME COLUMN created_at TO created_time;
ALTER TABLE app_developers RENAME COLUMN updated_at TO updated_time;

ALTER TABLE app_manifests RENAME COLUMN created_at TO created_time;
ALTER TABLE app_manifests RENAME COLUMN updated_at TO updated_time;

ALTER TABLE app_versions RENAME COLUMN created_at TO created_time;
ALTER TABLE app_versions RENAME COLUMN updated_at TO updated_time;

ALTER TABLE app_listings RENAME COLUMN created_at TO created_time;
ALTER TABLE app_listings RENAME COLUMN updated_at TO updated_time;

ALTER TABLE app_installations RENAME COLUMN created_at TO created_time;
ALTER TABLE app_installations RENAME COLUMN updated_at TO updated_time;

ALTER TABLE app_tools RENAME COLUMN created_at TO created_time;
ALTER TABLE app_tools RENAME COLUMN updated_at TO updated_time;

ALTER TABLE app_resources RENAME COLUMN created_at TO created_time;
ALTER TABLE app_resources RENAME COLUMN updated_at TO updated_time;

ALTER TABLE app_events RENAME COLUMN created_at TO created_time;
ALTER TABLE app_events RENAME COLUMN updated_at TO updated_time;

ALTER TABLE app_reviews RENAME COLUMN created_at TO created_time;
ALTER TABLE app_reviews RENAME COLUMN updated_at TO updated_time;

ALTER TABLE app_entitlements RENAME COLUMN created_at TO created_time;
ALTER TABLE app_entitlements RENAME COLUMN updated_at TO updated_time;

ALTER TABLE app_agent_bindings RENAME COLUMN created_at TO created_time;
ALTER TABLE app_agent_bindings RENAME COLUMN updated_at TO updated_time;

-- 数据与审计表
ALTER TABLE app_data_records RENAME COLUMN created_at TO created_time;
ALTER TABLE app_data_records RENAME COLUMN updated_at TO updated_time;

ALTER TABLE app_permission_audit_logs RENAME COLUMN created_at TO created_time;
