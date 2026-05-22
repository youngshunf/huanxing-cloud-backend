-- 修改 hasn_messages.local_id 字段类型从 UUID 改为 VARCHAR(100)
-- 原因：客户端发送的 local_id 不一定是 UUID 格式，如 local_1779427042848_xjputg

-- 删除旧的 UUID 类型约束
ALTER TABLE hasn_messages
ALTER COLUMN local_id TYPE VARCHAR(100)
USING local_id::VARCHAR(100);

COMMENT ON COLUMN hasn_messages.local_id IS '客户端本地 ID（用于去重，不限格式）';
