-- 为 sys_user.nickname 添加唯一约束（允许 NULL，用于未完善的账号）
CREATE UNIQUE INDEX CONCURRENTLY idx_sys_user_nickname_unique
ON sys_user (nickname)
WHERE nickname IS NOT NULL AND nickname != '';

-- 为 hasn_humans.nickname 添加唯一约束（与 sys_user 保持一致）
CREATE UNIQUE INDEX CONCURRENTLY idx_hasn_humans_nickname_unique
ON hasn_humans (nickname)
WHERE nickname IS NOT NULL AND nickname != '';

-- 添加注释
COMMENT ON INDEX idx_sys_user_nickname_unique IS '昵称唯一性约束（排除空值）';
COMMENT ON INDEX idx_hasn_humans_nickname_unique IS '昵称唯一性约束（排除空值）';
