-- 20260425 · 扩宽 hasn_contacts 的 *_id 列宽 36 → 40
--
-- Bug：原 schema 把 owner_id / peer_id / peer_owner_id 设为 varchar(36)，
-- 按裸 UUID 长度计算。但 HASN 实际 id 是 `<prefix>_<UUID>` 形式
-- （如 `a_e0fbe4d8-3f6f-40aa-ad3c-4d0d4f836739` = 38 字符），
-- 插入时报 StringDataRightTruncationError。
--
-- 与 hasn_agents.hasn_id (varchar(40)) 对齐到 40。
-- 幂等：用 ALTER ... TYPE，多次执行无副作用。

ALTER TABLE hasn_contacts
    ALTER COLUMN owner_id TYPE varchar(40),
    ALTER COLUMN peer_id TYPE varchar(40),
    ALTER COLUMN peer_owner_id TYPE varchar(40);
