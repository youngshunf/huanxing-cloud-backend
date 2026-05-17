-- 回滚昵称唯一性约束
DROP INDEX CONCURRENTLY IF EXISTS idx_sys_user_nickname_unique;
DROP INDEX CONCURRENTLY IF EXISTS idx_hasn_humans_nickname_unique;
