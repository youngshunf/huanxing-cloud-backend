-- 唤星服务器表新增 instance_type 字段
-- 区分实例类型: server（云端服务器）/ desktop（桌面端）/ mobile（移动端）
-- 2026-03-28

ALTER TABLE huanxing_server
ADD COLUMN IF NOT EXISTS instance_type VARCHAR(20) NOT NULL DEFAULT 'server';

COMMENT ON COLUMN huanxing_server.instance_type IS '实例类型: server/desktop/mobile';
